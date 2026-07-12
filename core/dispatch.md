# RDL Core — Adaptive Dispatch (D)

Each **phase** `κ` is a formal DOF-reducer with a contract `⟨pre, reduction, post, accept⟩` where
`post ⇒ (|W′| < |W|)` or a Terminal classification, and `accept` is a mechanically checkable
postcondition. The phase contracts live in `skills/research-development-loop/phases/<κ>.md`.

A phase is carried out by binding it to a **capability** — a tool, skill, dependency, permission,
or resource that is `granted ∩ present` (the manifest's usability relation). Binding is adaptive
and open-ended, never hardcoded. For each phase, bind at runtime to the **best available** capable
skill whose contract matches, discovered from the (open-ended) available-skills set injected into
context. Precedence:

```
most-specific available skill  ≻  the RDL's own fallback method for the phase  ≻  prompt
                                                                  (UNDECIDABLE — non-essential:
                                                                   name the missing capability)
```

`superpowers:<x>`, when present, is **one admissible binding** — never a dependency, never
forbidden. Any capable skill (built-in, plugin, or local) may satisfy a phase if its contract
matches; the loop **uses what is present** and falls back to its own method only when nothing
capable is installed. It NEVER forbids a skill that may or may not be installed.

**Record every binding** (`phase → skill@source`) so the run is reproducible: which capability
satisfied which phase, and the `accept` evidence it produced. A phase with no available capable
skill and no local fallback is an UNDECIDABLE — non-essential gap (prompt for the missing
capability), never a silent skip.
