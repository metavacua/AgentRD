# Export inventory — `wasm32v1-none` cdylib

The export surface is as load-bearing as the import surface: **imports = authority
requested; exports = the interface the witness provides.** A capability, in this witness
model, is a host-function *import*; a module with **zero imports** is provably powerless
(the hard gate). The exports define which ports the module inhabits.

## The general surface of any `wasm32v1-none` cdylib

Every `crate-type = ["cdylib"]` built for `wasm32v1-none` (release) exports, by default:

| export | kind | origin | meaning |
|---|---|---|---|
| `memory` | memory | compiler-emitted | the module's single linear memory (index 0) |
| `__data_end` | global | compiler-emitted | end-of-static-data address (ABI layout) |
| `__heap_base` | global | compiler-emitted | start-of-heap address (ABI layout) |

Everything else is the module's own declared surface — each `#[no_mangle] pub extern "C"`
item becomes a `(func …)` export. Nothing else is emitted: no `_start`, no table, no
`__wasm_call_ctors` for a leaf `no_std` crate with no static initializers.

Regenerate this inventory for any module with:
```
wasm-tools print <module>.wasm | grep -E '\(export'
wasm-tools print <module>.wasm | grep -E '\(import'   # authority — want empty
```

## This witness (`rdl-wasm`)

Declared interface (the abstract RDL core's ports, one `func` export each):

| export | signature (i32) | mirrors `schema.py` |
|---|---|---|
| `usable(granted, present) -> i32` | `U = G ∩ E` | `schema.usable` |
| `diagnose(granted, present) -> i32` | 0=ok 1=need-grant 2=need-install 3=need-both | `schema.diagnose` |
| `gate(granted, critical) -> i32` | 0=run 1=skip 2=prompt | `schema.gate` |
| `classify_terminal(inconsistent, undecidable, essential, is_inequality, feasible, determined) -> i32` | 0=DETERMINED 1=FEASIBLE 2=INCONSISTENT 3=UNDECIDABLE-nonessential 4=UNDECIDABLE-essential -1=not-terminal | `core/terminal.md` |
| `dof_step_ok(f_before, f_after, activated, classified) -> i32` | 1 iff `ΔF ≤ 0` ∨ activated ∨ classified | `core/invariant.md` |

Plus the three compiler-emitted defaults above. **Imports: none.** `test_wasm_gate.py`
enforces this inventory and the zero-import gate.
