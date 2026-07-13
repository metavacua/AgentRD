"""The orchestrator: AlphaZero-MCTS over wasm32v1-none node-objects, an evolutionary
outer loop over reasoning-paradigm genomes, and Inference-Time-Computing escalation.

Paradigm -> role mapping (all nine of the requested strategies):
  CoT / ReAct / Skeleton-of-Thought / ReSum ...... node-type genomes (the EA population)
  Imagine-Evaluate-Act ........................... a node's expand+evaluate step
  Tree of Thoughts ............................... the MCTS tree over node-objects
  Inference-Time Computing ....................... the escalation lever (tier ladder)
  Plan-Then-Execute .............................. the spec<-test<-code order = evolve() loop
  Agentic Workflows .............................. this harness (the hands)
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Protocol

from . import wasm

C_PUCT = 1.4

# paradigm -> (max branching, required capabilities). CoT is pure (leaf); the rest reason+act.
PARADIGMS = {
    "cot": (1, ()),
    "react": (2, ("spawn",)),
    "tot": (3, ("spawn",)),
    "sot": (4, ("spawn",)),
    "resum": (2, ("spawn",)),
}
TIERS = ("cheap", "mid", "expensive")  # the Inference-Time-Computing ladder


@dataclass(frozen=True)
class Genome:
    paradigm: str = "cot"
    tier: int = 0

    def branching(self) -> int:
        return PARADIGMS[self.paradigm][0]

    def requires(self) -> tuple:
        return PARADIGMS[self.paradigm][1]


class SpawnPort(Protocol):
    """The hexagonal port: an adapter (subagent, or a deterministic stub) supplying the
    AlphaZero policy (expansion) and value (evaluation) for a node."""
    def policy(self, state: int, genome: Genome) -> list[tuple[int, float]]: ...
    def value(self, state: int, genome: Genome) -> float: ...


@dataclass
class Node:
    state: int
    prior: float
    parent: "Node | None" = None
    N: int = 0
    W: float = 0.0
    children: list["Node"] = field(default_factory=list)
    expanded: bool = False

    @property
    def q(self) -> float:
        return self.W / self.N if self.N else 0.0


def _puct(node: Node) -> float:
    # Cross-witness-verified equal to rdl-wasm `node_puct` (tests/test_wasm_gate.py).
    npar = node.parent.N if node.parent else node.N
    return node.q + C_PUCT * node.prior * math.sqrt(max(1, npar)) / (1 + node.N)


def authorize(genome: Genome, granted: set[str]) -> bool:
    """Deny-by-default, enforced by the wasm gate: every required capability must gate to
    'run' (0). An ungranted capability gates to 'prompt'/'skip' -> denied."""
    return all(wasm.gate(cap in granted, critical=True) == 0 for cap in genome.requires())


def _all(root: Node) -> list[Node]:
    out, stack = [], [root]
    while stack:
        n = stack.pop()
        out.append(n)
        stack.extend(n.children)
    return out


def mcts(root_state: int, genome: Genome, port: SpawnPort, granted: set[str], budget: int) -> dict:
    """One AlphaZero-MCTS search with a fixed genome. Returns best Q and the winning state."""
    if not authorize(genome, granted):
        return {"fitness": 0.0, "denied": list(genome.requires()), "best_state": None, "nodes": 0}
    root = Node(root_state, 1.0)
    for _ in range(budget):
        node = root
        while node.expanded and node.children:                      # select (PUCT)
            node = max(node.children, key=_puct)
        if not node.expanded:                                       # expand (policy port)
            kids = port.policy(node.state, genome)[: genome.branching()]
            tot = sum(max(1e-3, p) for _, p in kids) or 1.0
            node.children = [Node(s, max(1e-3, p) / tot, parent=node) for s, p in kids]
            node.expanded = True
        v = port.value(node.state, genome)                          # evaluate (value port)
        cur = node
        while cur:                                                  # backprop
            cur.W += v
            cur.N += 1
            cur = cur.parent
    best = max(_all(root), key=lambda n: n.q)
    return {"fitness": round(best.q, 6), "best_state": best.state, "nodes": len(_all(root))}


def evolve(root_state: int, port: SpawnPort, granted: set[str], *, budget: int = 8,
           generations: int = 6, seed: int = 0, escalate_after: int = 1,
           threshold: float = 0.9) -> dict:
    """Evolutionary outer loop with Inference-Time-Computing escalation.

    Cheapest tier first. When the best fitness stalls below `threshold` for `escalate_after`
    generations, raise the tier cap (escalate to a more expensive model / more inference-time
    compute) — the 'swarm outclassed -> escalate' mechanism.
    """
    rng = random.Random(seed)
    pop = [Genome("cot", 0), Genome("react", 0), Genome("tot", 0)]
    tier_cap, stall = 0, 0
    best_overall = {"fitness": 0.0, "genome": None}
    history = []
    for gen in range(generations):
        scored = []
        for g in pop:
            g = Genome(g.paradigm, min(g.tier, tier_cap))           # respect the escalation cap
            r = mcts(root_state, g, port, granted, budget)
            scored.append((r["fitness"], g, r))
        scored.sort(key=lambda x: -x[0])
        top_fit, top_g, _ = scored[0]
        rec = {"gen": gen, "best_fit": top_fit, "genome": (top_g.paradigm, TIERS[top_g.tier]),
               "tier_cap": TIERS[tier_cap]}
        if top_fit > best_overall["fitness"]:
            best_overall = {"fitness": top_fit, "genome": (top_g.paradigm, top_g.tier)}
            stall = 0
        else:
            stall += 1
        if top_fit < threshold and stall >= escalate_after and tier_cap < len(TIERS) - 1:
            tier_cap += 1                                            # ESCALATE (Inference-Time Computing)
            stall = 0
            rec["escalated_to"] = TIERS[tier_cap]
        history.append(rec)
        survivors = [s[1] for s in scored[:2]]                      # select
        pop = survivors + [_mutate(rng, survivors[0], tier_cap)]    # + mutate
    return {"best": best_overall, "history": history, "final_tier_cap": TIERS[tier_cap]}


def _mutate(rng: random.Random, g: Genome, tier_cap: int) -> Genome:
    if rng.random() < 0.5:
        return Genome(rng.choice(list(PARADIGMS)), min(g.tier, tier_cap))
    return Genome(g.paradigm, min(g.tier + 1, tier_cap))
