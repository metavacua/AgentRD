# Guardrail: the orchestrator must forbid discretionary, effort-based deferral of
# in-scope work. Root cause of a real Phase-5 finding (2026-07-12): proportionality
# was used as a skip reason, which the chain's own Rice-correct principle forbids.
from pathlib import Path

ORCH = (Path("/home/metavacua/.claude/skills/research-development-loop") / "SKILL.md").read_text()
LOW = ORCH.lower()


def test_proportionality_is_not_a_valid_skip_reason():
    # Effort / proportionality / triviality must be NAMED as an invalid basis for skipping.
    assert "proportionalit" in LOW
    assert "rice" in LOW  # ties the rule to the chain's stated Rice-correct principle


def test_scope_reduction_requires_explicit_user_assertion():
    assert "explicit user assertion" in LOW or "user-asserted" in LOW


def test_only_missing_grant_justifies_a_skip():
    # The one legitimate skip axis is a missing capability grant, not agent judgment.
    assert "missing" in LOW and "grant" in LOW


def test_deferred_inventory_item_must_cite_grant_or_user_assertion():
    # Phase 5's negative-inventory "deferred" category may not rest on agent discretion.
    assert "agent discretion" in LOW  # named as a false-clean
