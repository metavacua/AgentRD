# RDL Core — Adaptive Dispatch (D)

Each phase is a **capability** `κ` — a formal DOF-reducer with a contract
`⟨pre, reduction, post, accept⟩` where `post ⇒ (|W′| < |W|)` or a Terminal classification, and
`accept` is a mechanically checkable postcondition. The canonical capabilities live in
`skills/research-development-loop/capabilities/<κ>.md`.

**Binding is adaptive and open-ended, never hardcoded.** For each `κ`, bind at runtime to the
**best available** skill whose contract matches, discovered from the (open-ended) available-skills
set injected into context. Precedence:

```
most-specific available skill  ≻  RDL's own capability module  ≻  prompt
                                                                   (UNDECIDABLE — non-essential:
                                                                    name the missing capability)
```

`superpowers:<x>`, when present, is **one admissible binding** of the matching `κ` — never a
dependency, never erased. Any capable skill (built-in, plugin, or local) may satisfy `κ` if its
contract matches.

**Record every binding** (`κ → skill@source`) so the run is reproducible: which skill satisfied
which capability, and the `accept` evidence it produced. A capability with no available binding
and no local module is an UNDECIDABLE — non-essential gap (prompt for the missing capability),
never a silent skip.
