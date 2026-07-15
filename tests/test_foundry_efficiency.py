import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "foundry_efficiency", Path(__file__).parents[1] / "tools" / "foundry_efficiency.py"
)
efficiency = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(efficiency)

JOB = "50c8e4391849"
SESSION = f"cron_{JOB}_20260714_222527"


def line(at, component, message, session=SESSION):
    return f"{at} INFO [{session}] {component}: {message}"


class FoundryEfficiencyTests(unittest.TestCase):
    def test_first_turn_excludes_background_review(self):
        rows = [
            line("2026-07-14 22:25:27,619", "agent.turn_context", "conversation turn: history=0"),
            line("2026-07-14 22:25:31,637", "agent.conversation_loop", "API call #1: model=m provider=custom in=100 out=20 total=120 latency=3.9s"),
            line("2026-07-14 22:25:38,710", "agent.conversation_loop", "API call #2: model=m provider=custom in=150 out=30 total=180 latency=6.9s"),
            line("2026-07-14 22:30:47,453", "agent.conversation_loop", "Turn ended: reason=text_response(finish_reason=stop) model=m api_calls=2/100 budget=2/100"),
            line("2026-07-14 22:30:47,484", "agent.turn_context", "conversation turn: background review"),
            line("2026-07-14 22:31:01,606", "agent.conversation_loop", "API call #1: model=m provider=custom in=9000 out=900 total=9900 latency=14.1s"),
            line("2026-07-14 22:36:29,670", "agent.conversation_loop", "Turn ended: reason=max_iterations_reached(16/16) model=m api_calls=16/16 budget=16/16"),
        ]
        parsed = efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7")
        self.assertEqual(len(parsed), 1)
        run = parsed[0]
        self.assertEqual(run["api_call_count"], 2)
        self.assertEqual(run["sum_input_tokens"], 250)
        self.assertEqual(run["sum_output_tokens"], 50)
        self.assertEqual(run["final_input_tokens"], 150)
        self.assertEqual(run["reported_api_calls"], 2)
        self.assertEqual(run["status"], "complete")
        self.assertTrue(run["first_turn_only"])

    def test_duplicate_api_line_is_counted_once(self):
        api = line("2026-07-14 22:25:31,637", "agent.conversation_loop", "API call #1: model=m provider=custom in=100 out=20 total=120 latency=3.9s")
        rows = [
            line("2026-07-14 22:25:30,000", "agent.turn_context", "conversation turn: session=x history=0"),
            api, api,
            line("2026-07-14 22:25:32,000", "agent.conversation_loop", "Turn ended: reason=stop model=m api_calls=1/4 budget=1/4"),
        ]
        parsed = efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7")
        self.assertEqual(parsed[0]["api_call_count"], 1)
        self.assertEqual(parsed[0]["sum_total_tokens"], 120)

    def test_terminal_durations_are_trusted_and_deduplicated(self):
        expensive = line(
            "2026-07-14 22:25:33,000", "agent.tool_executor",
            "tool terminal completed (97.93s, 374 chars)",
        )
        rows = [
            line("2026-07-14 22:25:30,000", "agent.turn_context", "conversation turn: session=x history=0"),
            line("2026-07-14 22:25:31,637", "agent.conversation_loop", "API call #1: model=m provider=custom in=100 out=20 total=120 latency=3.9s"),
            expensive,
            expensive,
            line("2026-07-14 22:25:34,000", "agent.tool_executor", "Tool terminal returned error (0.08s, 80 chars)"),
            line("2026-07-14 22:25:35,000", "agent.conversation_loop", "Turn ended: reason=stop model=m api_calls=1/4 budget=1/4"),
        ]
        run = efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7")[0]
        self.assertEqual(run["terminal_call_count"], 2)
        self.assertEqual(run["expensive_terminal_call_count"], 1)
        self.assertEqual(run["expensive_terminal_calls"][0]["duration_seconds"], 97.93)
        self.assertAlmostEqual(run["sum_terminal_seconds"], 98.01)

    def test_timed_out_terminal_is_counted_as_expensive(self):
        lines = [
            line(
                "2026-07-14 01:00:00,000", "agent.turn_context",
                "conversation turn: session=x history=0",
            ),
            line(
                "2026-07-14 01:00:01,000", "agent.conversation_loop",
                "API call #1: model=m in=10 out=2 total=12 latency=1.0s",
            ),
            line(
                "2026-07-14 01:02:01,000", "agent.tool_executor",
                'Tool terminal returned error (120.21s): {"exit_code": 124}',
            ),
            line(
                "2026-07-14 01:02:02,000", "agent.conversation_loop",
                "Turn ended: reason=done model=x api_calls=1/18",
            ),
        ]
        run = efficiency.parse_log_lines(lines, {JOB}, "Etc/GMT+7")[0]
        self.assertEqual(run["terminal_call_count"], 1)
        self.assertEqual(run["expensive_terminal_call_count"], 1)
        self.assertEqual(run["expensive_terminal_calls"][0]["outcome"], "returned_error")
        self.assertAlmostEqual(run["sum_terminal_seconds"], 120.21)

    def test_incomplete_turn_remains_visible(self):
        rows = [
            line("2026-07-14 23:02:12,100", "agent.turn_context", "conversation turn: session=x history=0"),
            line("2026-07-14 23:02:21,424", "agent.conversation_loop", "API call #1: model=m provider=custom in=19311 out=225 total=19536 latency=8.8s"),
        ]
        parsed = efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7")
        self.assertEqual(parsed[0]["status"], "incomplete")
        self.assertIsNone(parsed[0]["ended_at"])

    def test_job_filter(self):
        other = "cron_aaaaaaaaaaaa_20260714_222527"
        rows = [
            line("2026-07-14 22:25:30,000", "agent.turn_context", "conversation turn: session=x history=0", other),
            line("2026-07-14 22:25:31,637", "agent.conversation_loop", "API call #1: model=m provider=custom in=1 out=1 total=2 latency=1.0s", other),
        ]
        self.assertEqual(efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7"), [])

    def test_truncated_background_only_log_is_ignored(self):
        rows = [
            line("2026-07-14 22:31:01,606", "agent.turn_context", "conversation turn: session=x history=34 msg='Review the conversation'"),
            line("2026-07-14 22:31:02,000", "agent.conversation_loop", "API call #1: model=m provider=custom in=9000 out=900 total=9900 latency=14.1s"),
            line("2026-07-14 22:36:29,670", "agent.conversation_loop", "Turn ended: reason=stop model=m api_calls=1/16 budget=1/16"),
        ]
        self.assertEqual(efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7"), [])

    def test_receipt_match_converts_fixed_mst_to_utc(self):
        rows = [
            line("2026-07-14 22:25:30,000", "agent.turn_context", "conversation turn: session=x history=0"),
            line("2026-07-14 22:25:31,637", "agent.conversation_loop", "API call #1: model=m provider=custom in=100 out=20 total=120 latency=3.9s"),
            line("2026-07-14 22:30:47,453", "agent.conversation_loop", "Turn ended: reason=stop model=m api_calls=1/4 budget=1/4"),
        ]
        sessions = efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7")
        receipts = [{
            "receipt_id": "sha256:" + "a" * 64,
            "occurred_at": "2026-07-15T05:30:47Z",
            "frontier_id": "erdos_21_q6",
            "classification": "progress",
            "evidence_class": "provisional",
            "source": {"job_id": JOB, "sha256": "b" * 64},
        }]
        efficiency.attach_receipt_telemetry(sessions, receipts, 30)
        telemetry = sessions[0]["receipt_telemetry"]
        self.assertEqual(telemetry["frontier_id"], "erdos_21_q6")
        self.assertLess(telemetry["end_delta_seconds"], 1)
        self.assertTrue(telemetry["telemetry_only_not_reward"])

    def test_aggregate_refuses_to_invent_utility(self):
        rows = [
            line("2026-07-14 23:02:12,100", "agent.turn_context", "conversation turn: session=x history=0"),
            line("2026-07-14 23:02:21,424", "agent.conversation_loop", "API call #1: model=m provider=custom in=10 out=2 total=12 latency=1.0s"),
        ]
        sessions = efficiency.parse_log_lines(rows, {JOB}, "Etc/GMT+7")
        result = efficiency.aggregate(sessions)
        self.assertIsNone(result["utility_score"])
        self.assertEqual(result["sum_input_tokens"], 10)

    def test_atomic_report_is_private_before_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metrics.json"
            efficiency.atomic_json(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text()), {"ok": True})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
