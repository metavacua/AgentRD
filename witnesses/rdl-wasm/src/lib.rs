//! rdl-wasm — a `wasm32v1-none` witness of the abstract RDL core.
//!
//! Pure domain logic behind the hexagonal ports: capability resolution (U = G ∩ E),
//! the five-class terminal classification, and the DOF invariant. It is `no_std` and
//! imports NOTHING from a host, so — inspected with `wasm-tools` — it is provably
//! powerless: it cannot touch the filesystem, network, clock, or spawn anything.
//! A capability, in this witness, is a host-function *import*; absence of imports is
//! the hard gate. This mirrors `skills/research-development-loop/rdloop/schema.py`
//! (the markdown/python witness) so the two can be cross-checked.
#![no_std]

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    loop {}
}

/// Usability `U = G ∩ E`: 1 iff granted AND present, else 0.
#[no_mangle]
pub extern "C" fn usable(granted: i32, present: i32) -> i32 {
    ((granted != 0) && (present != 0)) as i32
}

/// Diagnose why a capability is unusable: 0=ok, 1=need-grant, 2=need-install, 3=need-both.
#[no_mangle]
pub extern "C" fn diagnose(granted: i32, present: i32) -> i32 {
    match (granted != 0, present != 0) {
        (true, true) => 0,
        (true, false) => 2,  // granted, absent  -> need-install
        (false, true) => 1,  // present, forbidden -> need-grant
        (false, false) => 3, // need-both
    }
}

/// Route an ungranted shell-out: 0=run, 1=skip, 2=prompt. Never silent.
#[no_mangle]
pub extern "C" fn gate(granted: i32, critical: i32) -> i32 {
    if granted != 0 {
        0
    } else if critical != 0 {
        2
    } else {
        1
    }
}

/// Terminal classification (core/terminal.md), from decidable flags.
/// 0=DETERMINED, 1=FEASIBLE, 2=INCONSISTENT, 3=UNDECIDABLE_NONESSENTIAL,
/// 4=UNDECIDABLE_ESSENTIAL, -1 = not yet a terminal state.
#[no_mangle]
pub extern "C" fn classify_terminal(
    inconsistent: i32,
    undecidable: i32,
    essential: i32,
    is_inequality: i32,
    feasible: i32,
    determined: i32,
) -> i32 {
    if inconsistent != 0 {
        2
    } else if undecidable != 0 {
        if essential != 0 {
            4
        } else {
            3
        }
    } else if is_inequality != 0 {
        if feasible != 0 {
            1
        } else {
            2 // empty feasible region == infeasible/inconsistent
        }
    } else if determined != 0 {
        0
    } else {
        -1
    }
}

/// DOF invariant (core/invariant.md): a step is legal iff it does not increase degrees
/// of freedom (ΔF ≤ 0), OR activates a constraint (inequality base case), OR classifies.
/// Returns 1 if legal, 0 if the step is a defect.
#[no_mangle]
pub extern "C" fn dof_step_ok(f_before: i32, f_after: i32, activated: i32, classified: i32) -> i32 {
    ((f_after <= f_before) || (activated != 0) || (classified != 0)) as i32
}

// ---------------------------------------------------------------------------
// Node-object ABI (Increment 2). Each MCTS node is a wasm32v1-none object; these
// are its pure AlphaZero-MCTS primitives. The Chain-of-Thought node is the leaf
// paradigm: genome 0, branching 1, zero imports (powerless by default).
// ---------------------------------------------------------------------------

/// Node genome tag. 0 = Chain-of-Thought (pure, linear).
#[no_mangle]
pub extern "C" fn node_kind() -> i32 {
    0
}

/// Max branching factor of this node-type. CoT is a linear chain: 1.
#[no_mangle]
pub extern "C" fn node_branching() -> i32 {
    1
}

/// AlphaZero PUCT selection score: `Q + c_puct · P · √N_parent / (1 + N)`.
#[no_mangle]
pub extern "C" fn node_puct(q: f64, prior: f64, n: i32, n_parent: i32) -> f64 {
    const C_PUCT: f64 = 1.4;
    let np = if n_parent < 1 { 1 } else { n_parent } as f64;
    q + C_PUCT * prior * libm::sqrt(np) / (1.0 + n as f64)
}

/// Mean action-value `Q = W / N` (0 when unvisited).
#[no_mangle]
pub extern "C" fn node_q(w: f64, n: i32) -> f64 {
    if n <= 0 {
        0.0
    } else {
        w / n as f64
    }
}

/// Value backprop: `Q` after adding one evaluation `v` — `(W + v) / (N + 1)`.
#[no_mangle]
pub extern "C" fn backprop_q(w: f64, n: i32, v: f64) -> f64 {
    (w + v) / (n as f64 + 1.0)
}

// The domain is verified against the ACTUAL wasm32v1-none artifact via wasmtime
// (see witnesses/rdl-wasm/tests/ and the Python gate-proof test), not a host recompile —
// the point is to exercise the gated module, not a std rebuild of it.
