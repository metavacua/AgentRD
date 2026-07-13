# Systematic-debugging (2026-07-13): the RDL loop was a NO-OP when constructing the
# rust/wasm/hexagonal witness. Two distinct actions are required and only one partially
# happened: (A) compile the rust WORKSPACE to wasm32v1-none, (B) execute the RDL phases
# (which must leave artifacts: a design/plan naming the feature with AC->task->test
# traceability). This test enforces both so witness construction cannot no-op the RDL.
import tomllib
from pathlib import Path

from _paths import REPO_ROOT


def test_action_a_rust_is_a_cargo_workspace_including_the_witness():
    ws = REPO_ROOT / "witnesses" / "Cargo.toml"
    assert ws.is_file(), "Action A incomplete: no cargo workspace at witnesses/Cargo.toml"
    m = tomllib.loads(ws.read_text())
    assert "workspace" in m, "witnesses/Cargo.toml is not a [workspace]"
    assert "rdl-wasm" in m["workspace"].get("members", []), "workspace does not include the witness crate"


def test_action_b_rdl_phases_left_a_traceable_plan_for_the_witness():
    plans_dir = REPO_ROOT / "docs" / "plans"
    hits = [p for p in plans_dir.glob("*.md")
            if any(k in p.read_text().lower() for k in ("wasm32v1-none", "rdl-wasm"))]
    assert hits, "Action B (RDL Phase 2) was a no-op: no plan doc names the wasm witness"
    text = hits[0].read_text()
    assert "AC-" in text, "the witness plan lacks AC->task->test traceability (the RDL's RTM was skipped)"


def test_action_b_rdl_left_a_design_spec_for_the_witness():
    specs_dir = REPO_ROOT / "docs" / "specs"
    hits = [p for p in specs_dir.glob("*.md")
            if any(k in p.read_text().lower() for k in ("wasm32v1-none", "hexagon", "rdl-wasm"))]
    assert hits, "Action B (RDL Phase 1) was a no-op: no design spec names the wasm/hexagonal witness"
