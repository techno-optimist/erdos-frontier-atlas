import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("materialize", Path(__file__).parents[1] / "foundry" / "materialize_frontiers.py")
materialize = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(materialize)


class MaterializerTests(unittest.TestCase):
    def test_new_seed_is_planned_and_existing_seed_is_idempotent(self):
        seed = {key: "x" for key in materialize.REQUIRED}
        seed.update(id="new", atlas_problem_id=21, priority=0.18)
        doc = {"seeds": [seed]}
        self.assertEqual(materialize.plan_materialization({"items": []}, doc)[0]["id"], "new")
        self.assertEqual(materialize.plan_materialization({"items": [{"id": "new"}]}, doc), [])

    def test_apply_is_atomic_and_preserves_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.json"
            original = {"items": [{"id": "old"}]}
            path.write_text(json.dumps(original))
            backup = materialize.apply_materialization(
                path, original, [{"id": "new"}], datetime(2026, 7, 15, tzinfo=timezone.utc),
            )
            self.assertEqual(json.loads(backup.read_text()), original)
            self.assertEqual([row["id"] for row in json.loads(path.read_text())["items"]], ["old", "new"])

    def test_missing_contract_field_fails_closed(self):
        with self.assertRaises(ValueError):
            materialize.plan_materialization({"items": []}, {"seeds": [{"id": "bad"}]})

    def test_unknown_atlas_problem_fails_closed(self):
        seed = {key: "x" for key in materialize.REQUIRED}
        seed.update(id="new", atlas_problem_id=21, priority=0.18)
        with self.assertRaises(ValueError):
            materialize.plan_materialization({"items": []}, {"seeds": [seed]}, {1, 2, 3})


if __name__ == "__main__":
    unittest.main()
