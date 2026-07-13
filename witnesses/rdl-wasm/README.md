# `rdl-wasm` — a `wasm32v1-none` witness of the abstract RDL core

The Research-Development-Loop has an **abstract interface** (hexagonal ports: the DOF
invariant, terminal classification, capability resolution, dispatch). The markdown/python
plugin is one **witness**. This crate is a second witness — **Rust, `wasm32v1-none`,
`no_std`** — where the *hard gate* is the compiler and linker, not a hook.

## The hard gate
A capability is a **host-function import**. This module imports **nothing**, so — verified
with `wasm-tools` — it is **provably powerless**: no filesystem, network, clock, threads, or
process spawning. `capability = granted ∩ present` stops being prose and becomes *"it links."*
Deny-by-default is the default: authority must be explicitly imported to exist.

## Layout (hexagonal)
- `src/lib.rs` — the pure **domain core** (no ports needed yet; pure functions).
- Ports/adapters (subagent-spawn, file I/O) come later, as explicit host imports — each one a
  capability that shows up in the import inventory.

## Build & verify
```
export PATH="$HOME/.cargo/bin:$PATH"
cargo build --release --target wasm32v1-none
wasm-tools print target/wasm32v1-none/release/rdl_wasm.wasm | grep '(import'   # empty = the gate holds
wasm-tools print target/wasm32v1-none/release/rdl_wasm.wasm | grep '(export'   # the interface + ABI defaults
wasmtime run --invoke usable target/wasm32v1-none/release/rdl_wasm.wasm 1 1     # -> 1
```
See `EXPORTS.md` for the full export inventory and `tests/test_wasm_gate.py` for the gate proof
(zero-imports + inventory + wasmtime execution + **cross-witness agreement with `schema.py`**).
