# BRAIN/tests/test_notation.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import check_notation as n

def test_ears_five_patterns():
    assert n.classify_ears("WHEN mute is selected THE laptop SHALL suppress audio") == "event"
    assert n.classify_ears("WHILE no card is present THE ATM SHALL display insert-card") == "state"
    assert n.classify_ears("IF the input is invalid THEN THE system SHALL reject it") == "unwanted"
    assert n.classify_ears("WHERE a GPU is fitted THE renderer SHALL enable SIMD") == "optional"
    assert n.classify_ears("THE service SHALL log every request") == "ubiquitous"

def test_ears_rejects_non_ears():
    assert n.classify_ears("the system should probably log stuff") is None
    assert n.is_ears("THE x SHALL y") is True
    assert n.is_ears("please make it fast") is False

def test_rfc2119_only_allcaps_is_normative():
    kws = n.normative_keywords("The system MUST retry but should not block")
    assert "MUST" in kws
    assert "SHOULD NOT" not in kws  # lowercase 'should not' is informal (RFC 8174)

def test_content_gating_thresholds():
    assert n.arch_section_required(1) is False
    assert n.arch_section_required(2) is True
    assert n.adr_required(1) is False
    assert n.adr_required(2) is True

def test_structurizr_action_gated():
    assert n.structurizr_action(True) == "render"                       # usable = granted ∧ present
    assert n.structurizr_action(False) == "skip:architecture-rendering-disabled"  # optional-dep skip names the feature

def test_plan_task_cites_live_ac():
    assert n.plan_task_cites_ac("implements AC-3 per ADR-1", ["AC-1", "AC-3"]) is True
    assert n.plan_task_cites_ac("implements AC-9", ["AC-1", "AC-3"]) is False  # dangling ref
    assert n.plan_task_cites_ac("no citation here", ["AC-1"]) is False
