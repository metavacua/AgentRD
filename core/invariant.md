# RDL Core — Invariant (I)

**R&D reduces degrees of freedom.** The loop state is a constraint system `S = (V, C)`: variables
`V` (open propositions, unbound decisions) and constraints `C` (equations/inequalities from the
manifest, the user, and gathered evidence). `F(S) = |V| − rank(C)` = degrees of freedom.

Every step MUST do one of:
1. **eliminate a free variable** (`ΔF ≤ 0`) — add an independent constraint that pins a variable;
2. **activate a constraint** — for an inequality system, move toward the feasible region's
   boundary/vertex (the base case where an inequality becomes an equality); or
3. **classify** the system (see Terminal), including recognizing **essential undecidability** —
   itself a valid terminal, not a DOF increase.

A step that introduces a free variable — unbounded prose, an ad-hoc exception, an unenforced
choice, a hedge — without doing (1)–(3) is a **defect**, not a deliverable. Hedging is declining
to solve: a variable left free, dressed as humility.
