"""The external OpenAI-manuscript index must validate and never move a status."""
import pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent

def test_openai_math_index_validates():
    p = subprocess.run([sys.executable, "tools/validate_openai_math.py"], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
