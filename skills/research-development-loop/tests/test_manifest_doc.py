from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema

DOC = Path(__file__).resolve().parents[1] / "references" / "manifest.md"

def test_doc_covers_every_required_section():
    text = DOC.read_text()
    for s in schema.REQUIRED_SECTIONS:
        assert f"[{s}]" in text, f"manifest.md does not document [{s}]"

def test_doc_states_skip_prompt_rule():
    text = DOC.read_text().lower()
    assert "logged skip" in text and "user prompt" in text and "never" in text
