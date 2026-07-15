import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location("deploy_jobs", Path(__file__).parents[1] / "foundry" / "deploy_jobs.py")
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)


class DeployTests(unittest.TestCase):
    def test_retry_budget_covers_observed_cold_model_restart(self):
        self.assertEqual(deploy.API_MAX_RETRIES, 8)
        self.assertEqual(deploy.SETTINGS["agent.api_max_retries"], "8")
        self.assertEqual(deploy.FOUNDRY_MAX_TURNS, 16)
        self.assertEqual(deploy.FOUNDRY_MAX_WALL_SECONDS, 900)
        self.assertEqual(deploy.FOUNDRY_FINALIZE_NO_TOOLS_AFTER, 13)
        config = json.loads((Path(__file__).parents[1] / "foundry" / "config.json").read_text())
        self.assertEqual(
            deploy.FOUNDRY_MAX_TURNS,
            config["runtime_budget"]["scheduled_job_max_turns"],
        )
        self.assertEqual(
            deploy.FOUNDRY_MAX_WALL_SECONDS,
            config["runtime_budget"]["max_wall_seconds"],
        )
        self.assertEqual(
            deploy.FOUNDRY_MAX_TURNS,
            config["milestone_policy"]["hard_stop_call"],
        )
        self.assertEqual(
            deploy.FOUNDRY_FINALIZE_NO_TOOLS_AFTER,
            config["milestone_policy"]["final_replay_call"],
        )
        self.assertLess(
            config["milestone_policy"]["receipt_deadline_call"],
            deploy.FOUNDRY_MAX_TURNS,
        )

    def test_runtime_install_is_atomic_and_digest_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.py"
            target = Path(tmp) / "nested" / "target.py"
            source.write_text("print('current')\n")
            with mock.patch.object(deploy, "INSTALLS", {source: [target]}):
                installed = deploy.install_runtime_files()
            self.assertEqual(target.read_text(), source.read_text())
            self.assertEqual(target.stat().st_mode & 0o777, 0o755)
            self.assertEqual(len(installed[str(target)]), 64)

    def test_prompt_suffixes_are_idempotent_and_trace_is_explicit(self):
        prompt = deploy.append_prompt_once(
            "base", "FOUNDRY RECURSION (operator-authorized)", deploy.SUFFIX
        )
        prompt = deploy.append_prompt_once(
            prompt, "FOUNDRY TRACE (required)", deploy.TRACE_SUFFIX
        )
        repeated = deploy.append_prompt_once(
            prompt, "FOUNDRY TRACE (required)", deploy.TRACE_SUFFIX
        )
        self.assertEqual(prompt, repeated)
        self.assertEqual(prompt.count("FOUNDRY TRACE (required)"), 1)
        self.assertIn("only the six labelled receipt crosses", prompt)
        runtime = deploy.append_prompt_once(
            prompt, "FOUNDRY HARD RUNTIME BUDGET", deploy.RUNTIME_SUFFIX
        )
        self.assertIn("more than one terminal action", runtime)

    def test_managed_prompt_upsert_replaces_stale_runtime_policy(self):
        stale = (
            "base\n\nFOUNDRY HARD RUNTIME BUDGET (operator-enforced): "
            "This job has at most 18 model calls.\n\n"
            "FOUNDRY TRACE (required): stale trace"
        )
        current = deploy.upsert_prompt_section(
            stale, "FOUNDRY HARD RUNTIME BUDGET", deploy.RUNTIME_SUFFIX
        )
        current = deploy.upsert_prompt_section(
            current, "FOUNDRY MILESTONE CONTRACT", deploy.MILESTONE_SUFFIX
        )
        repeated = deploy.upsert_prompt_section(
            current, "FOUNDRY MILESTONE CONTRACT", deploy.MILESTONE_SUFFIX
        )
        self.assertNotIn("at most 18 model", current)
        self.assertIn("at most 16 model", current)
        self.assertEqual(current.count("FOUNDRY HARD RUNTIME BUDGET"), 1)
        self.assertEqual(current.count("FOUNDRY MILESTONE CONTRACT"), 1)
        self.assertEqual(current, repeated)


if __name__ == "__main__":
    unittest.main()
