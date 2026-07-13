# Guardrail: the orchestrator must forbid discretionary, effort-based deferral of
# in-scope work. Root cause of a real Phase-5 finding (2026-07-12): proportionality
# was used as a skip reason. The only legitimate skip is an empirical incapability —
# a required capability that is not `granted AND present`.
from pathlib import Path
from _paths import SKILLS_ROOT

ORCH = (SKILLS_ROOT / "research-development-loop" / "SKILL.md").read_text()
LOW = ORCH.lower()


def test_proportionality_is_not_a_valid_skip_reason():
    # Effort / proportionality must be NAMED as an invalid basis for skipping.
    assert "proportionalit" in LOW


def test_scope_reduction_requires_explicit_user_assertion():
    assert "explicit user assertion" in LOW or "user-asserted" in LOW


def test_only_empirical_incapability_justifies_a_skip():
    # The one legitimate skip axis is a required capability not granted-and-present.
    assert "granted" in LOW and "present" in LOW
    assert "missing" in LOW


def test_deferred_inventory_item_must_cite_grant_or_user_assertion():
    # Phase 5's negative-inventory "deferred" category may not rest on agent discretion.
    assert "agent discretion" in LOW  # named as a false-clean
