# End-to-end tests for the AlphaZero-MCTS + evolutionary orchestrator over the
# wasm32v1-none node-objects. Deterministic (seeded); the wasm witness enforces the
# capability gate. Skips if the rust/wasm toolchain is absent.
import sys
from pathlib import Path

import pytest

CRATE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CRATE))
from orchestrator import core, wasm  # noqa: E402

pytestmark = pytest.mark.skipif(not wasm.available(),
                                reason="rust/wasm toolchain (cargo, wasmtime) not present")


class StubSpawnPort:
    """Deterministic policy/value. Toy problem: climb toward TARGET. A cheap tier CANNOT
    exceed a value cap (it 'can't see' the optimum); higher tiers lift the cap — so
    Inference-Time-Computing escalation is deterministically required to cross threshold."""

    def __init__(self, target=6, scale=16):
        self.target, self.scale = target, scale

    def policy(self, state, genome):
        return [(s, 1.0) for s in [state + 1, state - 1, state + 2, state - 2][: genome.branching()]]

    def value(self, state, genome):
        base = max(0.0, 1.0 - abs(state - self.target) / self.scale)
        cap = 0.6 + 0.2 * genome.tier          # tier0 -> .6, tier1 -> .8, tier2 -> 1.0
        return min(base, cap)


@pytest.fixture(scope="module", autouse=True)
def _built():
    wasm.build()  # the gate calls need the compiled witness


def test_mcts_converges_toward_target():
    port = StubSpawnPort(target=6)
    r = core.mcts(0, core.Genome("tot", 2), port, granted={"spawn"}, budget=12)
    assert r["best_state"] is not None
    assert r["fitness"] > 0.5                  # climbs toward the target


def test_capability_gate_denies_ungranted_via_wasm():
    port = StubSpawnPort()
    # ReAct requires the 'spawn' capability; deny-by-default when it is not granted.
    denied = core.mcts(0, core.Genome("react", 0), port, granted=set(), budget=6)
    assert denied.get("denied") == ["spawn"] and denied["fitness"] == 0.0
    # granted -> the wasm gate returns run(0) -> the search proceeds.
    ok = core.mcts(0, core.Genome("react", 0), port, granted={"spawn"}, budget=6)
    assert "denied" not in ok and ok["best_state"] is not None


def test_cot_needs_no_capability():
    port = StubSpawnPort()
    r = core.mcts(0, core.Genome("cot", 0), port, granted=set(), budget=8)  # pure, no grant needed
    assert "denied" not in r


def test_inference_time_escalation_when_swarm_outclassed():
    # tier caps 0.6 / 0.8 are both < threshold 0.9, so the cheap swarm is outclassed and
    # escalation MUST climb the tier ladder to cross the threshold.
    port = StubSpawnPort(target=6)
    res = core.evolve(0, port, granted={"spawn"}, budget=12, generations=6, seed=1, threshold=0.9)
    assert res["history"][0]["tier_cap"] == "cheap"            # cheapest-first
    assert any("escalated_to" in h for h in res["history"])    # escalation occurred
    assert res["final_tier_cap"] == "expensive"                # climbed the full ladder
    assert res["best"]["fitness"] > 0.6                        # exceeded the cheap-tier cap -> only via escalation
