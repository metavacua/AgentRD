# Guardrail: the state-machine diagram (and all prose outside the credit block) must
# name each phase's industry-standard METHOD, never the superpowers reference-impl
# skill. Root cause of a Phase-5 finding (2026-07-12, recursive loop): the prose was
# decoupled but the DOT diagram still named superpowers skills as the method, and no
# test caught it (test_no_hard_superpowers_invocation only matched `invoke superpowers:`).
from pathlib import Path

SK = (Path("/home/metavacua/.claude/skills/research-development-loop") / "SKILL.md").read_text()

CREDIT_START = "## Standards & reference implementations"
CREDIT_END = "## Extended References"
_i = SK.index(CREDIT_START)
_j = SK.index(CREDIT_END, _i)
CREDIT_BLOCK = SK[_i:_j]           # the one place the skill names are legitimately listed
ELSEWHERE = SK[:_i] + SK[_j:]      # everywhere else must name the standard, not the skill

# superpowers skills whose method was replaced by an inlined standard
STALE_SKILLNAMES = [
    "verification-before-completion",
    "systematic-debugging",
    "finishing-a-development-branch",
    "subagent-driven-development",
    "writing-skills",
    "skill-creator",
]


def test_reference_impl_skillnames_only_in_credit_block():
    hits = [s for s in STALE_SKILLNAMES if s in ELSEWHERE]
    assert not hits, f"superpowers reference-impl skill named as method outside the credit block: {hits}"


def _dot_block():
    return SK.split("```dot", 1)[1].split("```", 1)[0].lower()


def test_state_machine_names_the_standards():
    dot = _dot_block()
    assert "root-cause analysis" in dot or "root cause" in dot   # debug node
    assert "definition of done" in dot                            # verify node
    assert "github flow" in dot                                   # finish node
    assert "agent skills" in dot                                  # skill-gap edge


def test_state_machine_has_no_superpowers_skillname():
    dot = _dot_block()
    hits = [s for s in STALE_SKILLNAMES if s in dot]
    assert not hits, f"state-machine diagram still names superpowers skills: {hits}"
