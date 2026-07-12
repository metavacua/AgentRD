import json
from pathlib import Path
EVALS = Path("/home/metavacua/.claude/skills/rdl-brainstorming/evals/evals.json")

def test_parses():
    json.loads(EVALS.read_text())

def test_covers_valve_and_structurizr_and_traceability():
    names = [e["eval_name"] for e in json.loads(EVALS.read_text())["evals"]]
    for expected in ["valve-no-auto-triviality", "structurizr-skip-when-ungranted", "ac-task-test-traceability"]:
        assert expected in names
