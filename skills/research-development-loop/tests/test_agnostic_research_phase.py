from pathlib import Path
from _paths import SKILLS_ROOT

RP = SKILLS_ROOT / "research-phase" / "SKILL.md"
BANNED = ["metavacua", "babel-harness", "larql", "chrishayuk", "pi-harness"]

def test_no_hardcoded_identifiers():
    text = RP.read_text().lower()
    hits = [b for b in BANNED if b in text]
    assert not hits, f"research-phase still hardcodes: {hits}"

def test_git_context_gated_on_vcs():
    text = RP.read_text().lower()
    assert "vcs" in text and "git branch" in text  # git commands now conditional on vcs

def test_toolchain_gated_on_subprocess():
    text = RP.read_text()
    assert "[capabilities].subprocess" in text  # step 0.5 references grants

def test_states_skip_rule():
    text = RP.read_text().lower()
    assert "logged skip" in text or "log a skip" in text
