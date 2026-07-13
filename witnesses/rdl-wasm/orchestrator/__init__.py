"""AlphaZero-MCTS + evolutionary orchestrator over wasm32v1-none node-objects.

Hexagonal hybrid: the pure node math + the capability gate are the `rdl-wasm` witness
(the brain); subagent policy/value is a PORT (`SpawnPort`) provided by an adapter (the
hands). Reasoning paradigms are the evolutionary genome; Inference-Time Computing is the
escalation lever (cheapest model first, escalate when the swarm is outclassed).
"""
