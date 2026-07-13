from pathlib import Path
from _paths import SKILLS_ROOT
PLANW = SKILLS_ROOT / "rdl-writing-plans"

def test_frontmatter_name():
    assert "name: rdl-writing-plans" in (PLANW / "SKILL.md").read_text()

def test_requires_traceability():
    t = (PLANW / "SKILL.md").read_text().lower()
    assert "ac-n" in t and "adr-n" in t
    assert "failing-test" in t or "failing test" in t
    assert "shall" in t  # test asserts the AC's SHALL clause

def test_rfc2119_global_constraints():
    assert "rfc 2119" in (PLANW / "SKILL.md").read_text().lower()
