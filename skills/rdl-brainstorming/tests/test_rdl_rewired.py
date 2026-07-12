# Guardrails for the RDL chain's relationship to the `superpowers` plugin.
# Correct contract: the loop MUST NOT HARD-REQUIRE superpowers (or any specific
# external skill) — every phase has a fallback method, so the loop runs to
# completion with the plugin ABSENT. But it MAY (and should) ADAPTIVELY USE
# superpowers when it is present. Forbidding the use of a skill that may or may
# not be installed is wrong; the invariant is "no hard requirement", not "never used".
from pathlib import Path

SKILLS = Path("/home/metavacua/.claude/skills")
ORCH = (SKILLS / "research-development-loop" / "SKILL.md").read_text()
DISPATCH = (Path("/home/metavacua/AgentRD/core") / "dispatch.md").read_text()


def test_phase1_binds_rdl_brainstorming():
    assert "rdl-brainstorming" in ORCH


def test_phase2_binds_rdl_writing_plans():
    assert "rdl-writing-plans" in ORCH


def test_dispatch_is_adaptive_with_fallback():
    # The right invariant: bind the best AVAILABLE skill, fall back to the RDL's own
    # method when none is present, prompt only when neither exists. Not a name-ban.
    low = DISPATCH.lower()
    assert "available" in low                       # use what is present
    assert "fall back" in low or "fallback" in low or "own" in low  # survive absence
    assert "prompt" in low                          # only when no binding exists


def test_superpowers_is_an_admissible_binding_not_forbidden():
    # superpowers is named as one usable-when-present binding, never as forbidden or required.
    low = DISPATCH.lower()
    assert "superpowers" in low
    assert "one admissible binding" in low or "never a dependency" in low


def test_every_phase_has_an_inlined_fallback_method():
    # Because the loop must survive the plugin's absence, each phase's own method
    # (an industry standard) is present as the fallback.
    low = ORCH.lower()
    assert "root cause" in low or "root-cause" in low          # debug fallback
    assert "definition of done" in low                          # verify fallback
    assert "github flow" in low or "conventional commits" in low  # finish fallback
    assert "agent skills" in low                                # skill-authoring fallback
