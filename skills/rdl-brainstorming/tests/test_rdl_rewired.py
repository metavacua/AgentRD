# Guardrails for the RDL chain's decoupling from the `superpowers` plugin.
# Contract (user-approved): the loop MUST run to completion with the superpowers
# plugin ABSENT. `superpowers` MAY appear only as a credited reference implementation,
# never as an imperative invocation or an inheritance dependency.
import re
from pathlib import Path

SKILLS = Path("/home/metavacua/.claude/skills")
ORCH = (SKILLS / "research-development-loop" / "SKILL.md").read_text()
BRAIN = (SKILLS / "rdl-brainstorming" / "SKILL.md").read_text()
PLANS = (SKILLS / "rdl-writing-plans" / "SKILL.md").read_text()
CHAIN_TEXT = ORCH + "\n" + BRAIN + "\n" + PLANS

# Imperative invocation / hard-dependency phrasings that would re-couple the chain.
BANNED_INVOCATION = re.compile(
    r"\b(invoke|invoking|fall back to|call)\b[^\n]{0,40}superpowers:"
    r"|inherit[a-z]*\s+the\s+superpowers"
    r"|follow\s+the\s+superpowers[^\n]{0,40}verbatim",
    re.IGNORECASE)


def test_phase1_invokes_rdl_brainstorming():
    assert "rdl-brainstorming" in ORCH


def test_phase2_invokes_rdl_writing_plans():
    assert "rdl-writing-plans" in ORCH


def test_no_hard_superpowers_invocation():
    # The plugin must not be a required runtime dependency anywhere in the chain.
    hits = [m.group(0) for m in BANNED_INVOCATION.finditer(CHAIN_TEXT)]
    assert not hits, f"chain still hard-invokes/ inherits superpowers: {hits}"


def test_superpowers_still_credited_as_reference():
    # Lineage is preserved as an explicit credit, not silently erased.
    low = CHAIN_TEXT.lower()
    assert "superpowers" in low
    assert "reference implementation" in low


def test_industry_standards_inlined_in_orchestrator():
    low = ORCH.lower()
    # The mapped, verified standards must be present as the actual method.
    assert "root cause" in low or "root-cause" in low          # debugging
    assert "definition of done" in low                          # verification
    assert "github flow" in low or "conventional commits" in low  # finishing
    assert "agent skills" in low                                # skill authoring
