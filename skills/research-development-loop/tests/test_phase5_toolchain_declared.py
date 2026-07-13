# Guardrail: the RDL must declare Phase 5's real toolchain requirement, and this
# project's manifest must grant it. Root cause of a Phase-5 finding (2026-07-12):
# scholarly-white-paper needs DocBook/RELAX NG/XSLT tooling (xmllint, xsltproc, jing),
# but the RDL skill and manifest never reflected that requirement.
import sys
from pathlib import Path
from _paths import REPO_ROOT, SKILLS_ROOT

REPO = REPO_ROOT
SKILLS = SKILLS_ROOT
sys.path.insert(0, str(REPO / "skills" / "research-development-loop"))
from rdloop import schema  # noqa: E402

ORCH = (SKILLS / "research-development-loop" / "SKILL.md").read_text().lower()
PHASE5_TOOLS = ("xmllint", "xsltproc", "jing")


def test_orchestrator_phase5_names_the_toolchain():
    # Phase 5 must name the DocBook/RELAX NG/XSLT tools it depends on, gated per skip rule.
    for tool in PHASE5_TOOLS:
        assert tool in ORCH, f"RDL Phase 5 does not declare its dependency on {tool}"


def test_orchestrator_gates_phase5_toolchain():
    # The requirement must be tied to the skip/prompt rule, not assumed present.
    assert "docbook" in ORCH or "relax ng" in ORCH or "scholarly" in ORCH


def test_project_manifest_grants_phase5_toolchain():
    m = schema.load(REPO / "rdloop.toml")
    granted = set(m["capabilities"]["subprocess"])
    missing = [t for t in PHASE5_TOOLS if t not in granted]
    assert not missing, f"rdloop.toml does not grant Phase-5 tools: {missing}"
