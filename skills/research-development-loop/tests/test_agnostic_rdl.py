# RDL/tests/test_agnostic_rdl.py
from pathlib import Path
from _paths import SKILLS_ROOT

SK = SKILLS_ROOT / "research-development-loop" / "SKILL.md"
BANNED = ["metavacua", "babel-harness", "chrishayuk", "pi-harness", "larql",
          "ollama", "bin/coding-agent", "6.3 gb"]

def test_no_hardcoded_identifiers():
    text = SK.read_text().lower()
    hits = [b for b in BANNED if b in text]
    assert not hits, f"RDL SKILL.md still hardcodes: {hits}"

def test_loads_manifest_at_start():
    text = SK.read_text()
    assert "rdloop.toml" in text and "references/manifest.md" in text

def test_states_criticality_rule():
    t = SK.read_text().lower()
    assert "non-critical" in t and "critical" in t
    assert "logged skip" in t and "user prompt" in t
    assert "false-clean" in t or "silently" in t

def test_security_is_manifest_driven():
    text = SK.read_text()
    assert "[security]" in text or "[capabilities]" in text
