import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "patch_hermes_cron",
    Path(__file__).parents[1] / "foundry" / "patch_hermes_cron.py",
)
patcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patcher)


class HermesCronPatchTests(unittest.TestCase):
    @staticmethod
    def scheduler_source():
        return (
            "import logging\n"
            "logger = logging.getLogger(__name__)\n"
            "def run(job, _cfg, agent, _cron_future):\n"
            "    if True:\n"
            + patcher.OLD
            + "        job_name = 'fixture'\n"
            + "        def _make_agent(**kwargs): return agent\n"
            + "        _session_db = None\n"
            + "        agent = _make_agent(\n"
            + patcher.FINALIZE_OLD
            + "        _cron_timeout = 600.0\n"
            + patcher.WALL_SETUP_OLD
            + "        try:\n"
            + "            if False:\n"
            + "                pass\n"
            + "            else:\n"
            + "                while True:\n"
            + "                    done = {_cron_future}\n"
            + "                    import time\n"
            + "                    time.sleep(0.002)\n"
            + patcher.WALL_LOOP_OLD
            + "                    _idle_secs = 0.0\n"
            + "        except Exception:\n"
            + "            raise\n"
            + "        return max_iterations\n"
        )

    @staticmethod
    def loop_source():
        return (
            "def run_loop(agent, responses):\n"
            "    messages = []\n"
            "    api_call_count = 0\n"
            "    while api_call_count < agent.max_iterations:\n"
            "        api_call_count += 1\n"
            "        if True:\n"
            "            if True:\n"
            "                final_response = responses[api_call_count - 1]\n"
            "                assistant_message = {'content': final_response}\n"
            "                finish_reason = 'stop'\n"
            + patcher.LOOP_OLD
            + "                messages.append(final_msg)\n"
            + "                agent._session_messages = messages\n"
            + "                return final_response, api_call_count, messages\n"
            + "    return None, api_call_count, messages\n"
        )

    def test_patch_is_exact_idempotent_and_only_lowers_global_cap(self):
        original = self.scheduler_source()
        patched, changed = patcher.patch_text(original)
        self.assertTrue(changed)
        self.assertIn(patcher.MARKER, patched)
        self.assertIn(patcher.WALL_MARKER, patched)
        self.assertIn(patcher.FINALIZE_MARKER, patched)
        self.assertIn("min(_global_max_iterations", patched)
        repeated, changed_again = patcher.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(repeated, patched)

    def test_unknown_scheduler_source_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "source drifted"):
            patcher.patch_text("unrecognized scheduler")

    def test_existing_turn_patch_upgrades_to_wall_cap(self):
        source = self.scheduler_source().replace(patcher.OLD, patcher.NEW)
        patched, changed = patcher.patch_text(source)
        self.assertTrue(changed)
        self.assertEqual(patched.count(patcher.MARKER), 1)
        self.assertEqual(patched.count(patcher.WALL_MARKER), 1)

    def test_wall_cap_is_opt_in_and_fails_closed_on_invalid_values(self):
        namespace = {}
        patched, _ = patcher.patch_text(self.scheduler_source())
        exec(compile(patched, "scheduler.py", "exec"), namespace)

        class Agent:
            interrupted = None
            step_callback = None
            tools = [{"function": {"name": "terminal"}}]
            valid_tool_names = {"terminal"}
            _skill_nudge_interval = 5
            _pending_steer_lock = None
            _pending_steer = None

            def interrupt(self, reason):
                self.interrupted = reason

        class Future:
            def result(self):
                return {"ok": True}

        run = namespace["run"]
        self.assertEqual(run({}, {"agent": {"max_turns": 100}}, Agent(), Future()), 100)
        with self.assertRaisesRegex(RuntimeError, "finite positive"):
            run({"max_wall_seconds": 0}, {}, Agent(), Future())
        agent = Agent()
        with self.assertRaisesRegex(TimeoutError, "exceeded wall limit"):
            run({"max_wall_seconds": 0.001}, {}, agent, Future())
        self.assertEqual(agent.interrupted, "Cron job timed out (wall limit)")

    def test_no_tools_finalization_is_opt_in_and_preserves_other_jobs(self):
        namespace = {}
        patched, _ = patcher.patch_text(self.scheduler_source())
        exec(compile(patched, "scheduler.py", "exec"), namespace)

        class Agent:
            step_callback = None
            tools = [{"function": {"name": "terminal"}}]
            valid_tool_names = {"terminal"}
            _skill_nudge_interval = 5
            _pending_steer_lock = None
            _pending_steer = None

        class Future:
            def result(self): return {"ok": True}

        run = namespace["run"]
        plain = Agent()
        run({}, {"agent": {"max_turns": 16}}, plain, Future())
        self.assertIsNone(plain.step_callback)
        gated = Agent()
        run(
            {"max_turns": 16, "finalize_no_tools_after": 13},
            {"agent": {"max_turns": 90}}, gated, Future(),
        )
        gated.step_callback(13, [])
        self.assertTrue(gated.tools)
        gated.step_callback(14, [])
        self.assertEqual(gated.tools, [])
        self.assertEqual(gated.valid_tool_names, set())
        self.assertIn("six markdown labels", gated._pending_steer)
        with self.assertRaisesRegex(RuntimeError, "requires 0 <"):
            run(
                {"max_turns": 16, "finalize_no_tools_after": 16},
                {"agent": {"max_turns": 90}}, Agent(), Future(),
            )

    def test_file_install_preserves_backup_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scheduler.py"
            path.write_text(self.scheduler_source())
            path.chmod(0o640)
            result = patcher.patch_file(path)
            self.assertTrue(result["changed"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertTrue(Path(result["backup"]).exists())
            self.assertEqual(len(result["sha256"]), 64)

    def test_receipt_retry_is_exact_idempotent_and_preserves_plain_agents(self):
        original = self.loop_source()
        patched, changed = patcher.patch_loop_text(original)
        self.assertTrue(changed)
        self.assertIn(patcher.LOOP_MARKER, patched)
        repeated, changed_again = patcher.patch_loop_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(repeated, patched)
        namespace = {}
        exec(compile(patched, "conversation_loop.py", "exec"), namespace)

        class Agent:
            max_iterations = 3
            _foundry_required_final_labels = ()
            _foundry_finalize_after = None
            _foundry_finalization_retries = 0
            _foundry_finalization_retry_limit = 0

            @staticmethod
            def _strip_think_blocks(value): return value

            @staticmethod
            def _build_assistant_message(message, reason):
                return {"role": "assistant", "content": message["content"], "reason": reason}

        response, calls, messages = namespace["run_loop"](Agent(), ["plain"])
        self.assertEqual((response, calls), ("plain", 1))
        self.assertEqual(len(messages), 1)

    def test_receipt_retry_uses_reserved_calls_until_all_labels_exist(self):
        patched, _ = patcher.patch_loop_text(self.loop_source())
        namespace = {"logger": type("Log", (), {"info": staticmethod(lambda *args: None)})()}
        exec(compile(patched, "conversation_loop.py", "exec"), namespace)

        class Agent:
            max_iterations = 3
            _foundry_required_final_labels = (
                "Frontier", "Action", "Verified", "Result", "Next gate",
                "Boundary held",
            )
            _foundry_finalize_after = 0
            _foundry_finalization_retries = 0
            _foundry_finalization_retry_limit = 2

            @staticmethod
            def _strip_think_blocks(value): return value

            @staticmethod
            def _build_assistant_message(message, reason):
                return {"role": "assistant", "content": message["content"], "reason": reason}

        receipt = "\n".join(f"**{label}**\nvalue" for label in Agent._foundry_required_final_labels)
        agent = Agent()
        response, calls, messages = namespace["run_loop"](
            agent, ["intermediate", "still incomplete", receipt]
        )
        self.assertEqual((response, calls), (receipt, 3))
        self.assertEqual(agent._foundry_finalization_retries, 2)
        self.assertEqual(len(messages), 5)
        self.assertIn("all six required markdown labels", messages[1]["content"])
        self.assertIn("Frontier, Action, Verified", messages[1]["content"])

    def test_unknown_conversation_loop_source_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "source drifted"):
            patcher.patch_loop_text("unrecognized loop")

    def test_loop_file_install_preserves_backup_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "conversation_loop.py"
            path.write_text(self.loop_source())
            path.chmod(0o640)
            result = patcher.patch_loop_file(path)
            self.assertTrue(result["changed"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertTrue(Path(result["backup"]).exists())
            self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
