# RDL/tests/test_agnostic_references.py
from pathlib import Path
import re
from _paths import SKILLS_ROOT

REFDIR = SKILLS_ROOT / "research-development-loop" / "references"
BANNED = ["metavacua", "babel-harness", "chrishayuk", "pi-harness", "ollama", "larql"]
FILES = ["delegation.md", "issue-governance.md", "dependency-exploration.md", "hooks-architecture.md"]

def test_specifics_only_under_example_labels():
    for fname in FILES:
        text = (REFDIR / fname).read_text()
        for i, line in enumerate(text.splitlines()):
            low = line.lower()
            if any(b in low for b in BANNED):
                # allowed only on a line that (or whose block) is marked Example:
                assert "example" in low, f"{fname}:{i+1} has a specific outside an Example: {line!r}"
