import json
from pathlib import Path

EVALS = Path("/home/metavacua/.claude/skills/research-development-loop/evals/evals.json")

def test_evals_parse():
    json.loads(EVALS.read_text())

def test_no_hardcoded_repo_in_evals():
    text = EVALS.read_text().lower()
    for b in ["metavacua/babel-harness", "metavacua/larql-to-sparql"]:
        assert b not in text, f"eval still hardcodes {b}"

def test_bare_sandbox_eval_present():
    data = json.loads(EVALS.read_text())
    names = [e["eval_name"] for e in data["evals"]]
    assert "bare-sandbox-no-false-clean" in names

def test_bare_sandbox_eval_asserts_skip_not_false_clean():
    data = json.loads(EVALS.read_text())
    e = next(e for e in data["evals"] if e["eval_name"] == "bare-sandbox-no-false-clean")
    blob = json.dumps(e).lower()
    assert "logged skip" in blob or "log a skip" in blob
    assert "false-clean" in blob or "false clean" in blob
    assert "incapable" in blob and "halt" in blob  # required-missing halts, not skips
