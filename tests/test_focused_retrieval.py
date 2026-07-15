import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("focused", Path(__file__).parents[1] / "foundry" / "focused_retrieval.py")
focused = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(focused)


class FocusedRetrievalTests(unittest.TestCase):
    def test_rare_named_phrase_beats_common_single_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "atlas.db"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE thoughts(id TEXT, text TEXT, anchor TEXT)")
            con.executemany(
                "INSERT INTO thoughts VALUES(?,?,?)",
                [(str(i), "generic polynomial partition verifier search", "generic") for i in range(100)],
            )
            con.execute("INSERT INTO thoughts VALUES(?,?,?)", ("rare", "stretched Littlewood Richardson coefficient has a negative term", "representation theory"))
            con.commit(); con.close()
            rows = focused.focused_rows(db, "thoughts", "stretched Littlewood Richardson coefficient polynomial negative partition verifier", 5, ["text", "anchor"])
            self.assertEqual(rows[0]["id"], "rare")
            self.assertIn("littlewood richardson", rows[0]["matched_features"])
            self.assertIn("littlewood richardson", rows[0]["focus_excerpt"]["text"].lower())

    def test_excerpt_centers_a_deep_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "atlas.db"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE thoughts(id TEXT, text TEXT, anchor TEXT)")
            con.execute("INSERT INTO thoughts VALUES(?,?,?)", (
                "deep", "unrelated preface " * 100 + "Littlewood Richardson certificate" + " unrelated suffix" * 100, "representation theory",
            ))
            con.commit(); con.close()
            row = focused.focused_rows(db, "thoughts", "Littlewood Richardson", 1, ["text", "anchor"])[0]
            self.assertNotIn("littlewood richardson", row["text"].lower())
            self.assertIn("littlewood richardson", row["focus_excerpt"]["text"].lower())

    def test_read_only_hashes_stay_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            dbs = {}
            schemas = {
                "atlas": "CREATE TABLE thoughts(id TEXT, text TEXT, anchor TEXT)",
                "atlas2": "CREATE TABLE thoughts(id TEXT, text TEXT, anchor TEXT)",
                "arena": "CREATE TABLE problems(id TEXT, title TEXT, slug TEXT, scoring TEXT); CREATE TABLE concepts(id TEXT, canonical_name TEXT, description TEXT)",
                "aiwiki": "CREATE TABLE docs(id TEXT, title TEXT, text TEXT, aiwiki TEXT, record_key TEXT)",
            }
            for name, schema in schemas.items():
                path = Path(tmp) / f"{name}.db"; dbs[name] = path
                con = sqlite3.connect(path); con.executescript(schema); con.commit(); con.close()
            packet = focused.retrieve("Littlewood Richardson", dbs, 3)
            self.assertTrue(all(row["read_only_verified"] for row in packet["databases"].values()))

    def test_missing_database_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.db"
            packet = focused.retrieve("Littlewood Richardson", {
                "atlas": missing, "atlas2": missing, "arena": missing, "aiwiki": missing,
            }, 3)
            self.assertFalse(any(row["read_only_verified"] for row in packet["databases"].values()))


if __name__ == "__main__":
    unittest.main()
