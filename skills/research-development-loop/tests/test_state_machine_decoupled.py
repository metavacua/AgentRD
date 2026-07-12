# Guardrail: the state-machine diagram must name each phase's own METHOD (the
# industry-standard fallback that runs when no external skill is bound), so the
# loop is legible and survives the superpowers plugin's absence. It is NOT required
# to hide superpowers skill-names — adaptively using a present skill is correct; a
# name-ban would forbid the use of a skill that may or may not be installed.
from pathlib import Path

SK = (Path("/home/metavacua/.claude/skills/research-development-loop") / "SKILL.md").read_text()


def _dot_block():
    return SK.split("```dot", 1)[1].split("```", 1)[0].lower()


def test_state_machine_names_the_fallback_methods():
    dot = _dot_block()
    assert "root-cause analysis" in dot or "root cause" in dot   # debug node
    assert "definition of done" in dot                            # verify node
    assert "github flow" in dot                                   # finish node
    assert "agent skills" in dot                                  # skill-gap edge
