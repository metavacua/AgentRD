from pathlib import Path
SK = Path("/home/metavacua/.claude/skills/research-development-loop/SKILL.md").read_text()

def test_phase1_invokes_rdl_brainstorming():
    assert "rdl-brainstorming" in SK

def test_phase2_invokes_rdl_writing_plans():
    assert "rdl-writing-plans" in SK

def test_superpowers_process_still_credited():
    # inheritance is explicit, not a silent replacement
    low = SK.lower()
    assert "inherit" in low or "superpowers brainstorming process" in low
