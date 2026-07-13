# AlphaZero-MCTS + evolutionary sub-agent orchestrator

The complete hexagonal feature: an AlphaZero-MCTS search whose **nodes are `wasm32v1-none`
objects**, an **evolutionary** outer loop over reasoning-paradigm genomes, and
**Inference-Time-Computing escalation** (cheapest model first; escalate when the swarm is
outclassed). The capability gate is the powerless-by-default `rdl-wasm` witness.

## The nine paradigms, resolved into roles
| paradigm | role | where |
|---|---|---|
| Chain-of-Thought, ReAct, Skeleton-of-Thought, ReSum | node-type **genomes** (EA population) | `PARADIGMS` in `core.py` |
| Imagine-Evaluate-Act | a node's **expand+evaluate** step | `mcts()` select→policy→value |
| Tree of Thoughts | the **MCTS tree** over node-objects | `mcts()` |
| Inference-Time Computing | the **escalation lever** (tier ladder) | `evolve()` tier_cap |
| Plan-Then-Execute | the **spec≺test≺code order** | the build order + `evolve()` loop |
| Agentic Workflows | the **harness** (the hands) | this module |

## Hexagonal ports
- **Domain (brain)** — pure node math + capability gate: the `rdl-wasm` `wasm32v1-none`
  witness. `authorize()` routes every required capability through the wasm `gate()`
  (deny-by-default enforcement); PUCT is the cross-witness-verified Python equivalent.
- **Port** — `SpawnPort.policy/value`: the AlphaZero policy+value network per node.
- **Adapters (hands)**:
  - `StubSpawnPort` (in tests) — deterministic, for reproducible verification.
  - **Real subagent adapter** — a `SpawnPort` whose `policy`/`value` spawn Claude subagents
    (one per node, model/effort chosen by the genome's `tier`). Because subagent spawning is
    a harness capability (not callable from a unit test), the real adapter is driven from the
    agent/Workflow context; the orchestrator is otherwise identical.

## Usage
```python
from orchestrator import core
res = core.evolve(root_state, my_spawn_port, granted={"spawn"}, budget=8, generations=6)
# res["best"], res["history"] (per-gen tier/escalation), res["final_tier_cap"]
```
The genome's `tier` selects the model tier for its subagent adapter; `evolve()` starts at
the cheapest tier and escalates only when best-fitness stalls below `threshold` — the
"lowest-effort model first, escalate when outclassed" mechanism.

Tests: `tests/test_orchestrator.py` (MCTS convergence, wasm-gated capability denial,
deterministic ITC escalation).
