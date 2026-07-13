# Plan — rust / wasm32v1-none / hexagonal RDL witness (Phase 2, retroactive)

**Design:** `docs/specs/2026-07-13-rdl-wasm-hexagonal-witness-design.md` ·
**Feature crate:** `witnesses/rdl-wasm` (member of the `witnesses/` cargo workspace).

Retroactive per systematic-debugging (2026-07-13): the RDL's Phase-2 plan was a no-op when this
witness was built. This is the Requirements Traceability Matrix — **one AC → the task → the test**.

## Global Constraints (RFC 2119)
- The core MUST compile to `wasm32v1-none` and MUST declare zero host imports (the hard gate).
- Every capability decision MUST route through the wasm `gate()` (deny-by-default).
- Each task's behavior MUST be covered by a test that fails if the behavior is absent.

## Requirements Traceability Matrix (AC → task → test)

| AC | Task (increment) | Test (executable) |
|---|---|---|
| AC-1 | cargo **workspace** compiling the witness to `wasm32v1-none` | `test_witness_construction::test_action_a_rust_is_a_cargo_workspace_including_the_witness`; `test_wasm_gate` build fixture |
| AC-2 | Increment 1: gated core, **zero imports** | `test_wasm_gate::test_hard_gate_zero_imports` |
| AC-3 | Increment 2: node-object ABI + CoT node | `test_wasm_gate::test_node_object_abi_exports`, `test_cot_node_is_pure_and_linear`, `test_node_mcts_math_via_wasmtime` |
| AC-4 | Increment 3: capability port authorized via wasm `gate()` | `test_orchestrator::test_capability_gate_denies_ungranted_via_wasm` (red-green verified) |
| AC-5 | Increment 4: AlphaZero-MCTS (PUCT + backprop) over node-objects | `test_orchestrator::test_mcts_converges_toward_target`; `test_wasm_gate::test_cross_witness_puct` |
| AC-6 | Increment 5: EA + Inference-Time-Computing escalation | `test_orchestrator::test_inference_time_escalation_when_swarm_outclassed` |
| AC-7 | Increment 1/2: cross-witness agreement with `schema.py` | `test_wasm_gate::test_cross_witness_agreement_with_schema_py`, `test_cross_witness_puct` |

Every AC traces to at least one failing-first-then-green test. No AC is unverified; no test is
untethered. The enforcement test `test_witness_construction.py` guards that this plan (and the
design) exist and are traceable, so a future witness cannot be built by no-op'ing the RDL again.

## Known limitation (honesty mandate)
The **real subagent adapter** (AC-6's production binding) is harness-driven and has not been run —
only the deterministic `StubSpawnPort` is tested. This is the same limitation recorded in the
verification-before-completion pass; it is an integration seam, not a code gap.
