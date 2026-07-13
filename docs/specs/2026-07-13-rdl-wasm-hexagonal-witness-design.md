# Design — rust / wasm32v1-none / hexagonal RDL witness (retroactive, per systematic-debugging)

**Status:** design spec · **Date:** 2026-07-13 · **Feature:** `witnesses/rdl-wasm` — a Rust,
`wasm32v1-none`, hexagonal *witness* of the abstract RDL interface, with an AlphaZero-MCTS +
evolutionary sub-agent orchestrator.

> This spec was written *after* the code, during a systematic-debugging session: the root cause
> found was that the RDL loop was not executed when this witness was built (I used `/feature-dev`,
> not `/research-development-loop`), so its Phase-1 design and Phase-2 plan were no-ops. This file
> and the companion plan close that gap and are now enforced by `test_witness_construction.py`.

## Two distinct actions (the RDL for rust/wasm)
- **A — compile the rust *workspace* to target:** `witnesses/` is a cargo workspace; members
  compile to `wasm32v1-none`.
- **B — execute the RDL phases:** research → design (this file) → plan (companion) → develop (TDD) →
  verify → review, each leaving an artifact. Absence of these artifacts = the loop no-op'd.

## Acceptance criteria (EARS / RFC 2119)
- **AC-1** The witness SHALL compile to `wasm32v1-none` as a member of the `witnesses/` cargo workspace.
- **AC-2** WHEN the core is inspected, it SHALL declare **zero host imports** (zero ambient authority — the hard gate).
- **AC-3** Each MCTS node SHALL be a `wasm32v1-none` object exposing the pure node interface (`node_puct`, `node_q`, `backprop_q`, genome tags).
- **AC-4** A capability SHALL be usable only when `granted ∩ present`; an ungranted required capability SHALL be **denied** (deny-by-default) through the wasm `gate()`.
- **AC-5** The orchestrator SHALL search via AlphaZero-MCTS — PUCT selection + value backprop — over node-objects.
- **AC-6** The orchestrator SHALL evolve a population of reasoning-paradigm genomes and SHALL escalate the model tier WHEN the cheapest tier is outclassed (Inference-Time Computing).
- **AC-7** The witness's capability primitives SHALL agree with the `schema.py` witness (cross-witness consistency).

## Decisions (MADR)
- **ADR-1 — `wasm32v1-none` as the hard gate** (alternatives: a `PreToolUse` hook; honor-system prose).
  Chosen because incapability becomes a *compile/link* property — a module with zero imports is
  provably powerless — rather than a runtime check the model can ignore. Directly answers the MCTS
  audit's "unenforced core" finding.
- **ADR-2 — hexagonal *hybrid*** (alternatives: all-Rust host; all-in-harness). Pure logic + the
  capability gate compile to `wasm32v1-none`; subagent spawning is a harness-provided **port**,
  because spawning needs ambient authority a bare module cannot have.
- **ADR-3 — node-object ABI** (each node a `wasm32v1-none` object). Realizes "capability = host
  import" and "multiple witnesses of one abstract interface."

## Paradigm → role mapping
CoT/ReAct/SoT/ReSum = genomes; Imagine-Evaluate-Act = a node's expand+evaluate; Tree-of-Thoughts =
the MCTS tree; Inference-Time-Computing = the escalation lever; Plan-Then-Execute = the build order;
Agentic-Workflows = the harness.
