from pathlib import Path
from _paths import SKILLS_ROOT
BRAIN = SKILLS_ROOT / "rdl-brainstorming"

def test_frontmatter_name():
    text = (BRAIN / "SKILL.md").read_text()
    assert "name: rdl-brainstorming" in text

def test_declares_all_notation_sections():
    text = (BRAIN / "SKILL.md").read_text().lower()
    for token in ["dublin core", "schema.org", "rfc 2119", "ears", "structurizr", "madr", "glut register"]:
        assert token in text, f"SKILL.md missing '{token}'"

def test_valve_is_rice_correct():
    text = (BRAIN / "SKILL.md").read_text().lower()
    assert "non-trivial" in text and "content-gat" in text
    assert "must not" in text and "triviality" in text  # forbids auto-deciding triviality

def test_structurizr_only_no_rdf_architecture():
    text = (BRAIN / "SKILL.md").read_text().lower()
    assert "structurizr dsl only" in text

def test_notation_ref_lists_five_ears_patterns():
    text = (BRAIN / "references" / "notation.md").read_text().lower()
    for p in ["ubiquitous", "event-driven", "state-driven", "unwanted", "optional"]:
        assert p in text
