import importlib.util
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
        self.assertEqual(deploy.FOUNDRY_MAX_TURNS, 18)

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


if __name__ == "__main__":
    unittest.main()
