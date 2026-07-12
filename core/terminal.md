# RDL Core — Terminal Classification (T)

`S` is a system of **equations and inequalities**. The loop halts iff it classifies `S` as
**exactly one** row. Grounding: linear algebra (equalities); LP/convex duality (inequalities);
Gödel independence and MRDP/Hilbert's 10th (the undecidable cases).

| Class | Condition | Emit |
|---|---|---|
| **DETERMINED** | equality system, `rank(C) = |V|` | the unique solution → deliver |
| **FEASIBLE (optimizable)** | inequality system, region non-empty | reduce to the base case — solve the active-constraint (equality) boundaries; the optimum sits at a vertex where inequalities are tight. Deliver the optimum + the **binding** constraints. Not abdication. |
| **INFEASIBLE / INCONSISTENT** | empty region / glut (`rank[C] < rank[C|b]`) | the contradicting constraint pair + the rejected axiom |
| **UNDECIDABLE — non-essential** (a *gap*, `⊬P ∧ ⊬¬P`) | propositionally independent of current axioms; decidable in an extension | the **exact missing axiom** (observation/constraint/user input); the R&D action is to add it and re-solve |
| **UNDECIDABLE — essential** | undecidable in the theory *and every consistent extension* | name it and **halt** — no added observation decides it; further effort is provably wasted |

No other terminal states exist. "Done", "deferred", "logged skip", "N1…N4" are **not** terminal
states — each maps to a row above or is a defect. An "exception" is admissible only as the
*non-essential-undecidable* row, with its missing axiom named. A gap MUST be discharged as
non-essential (add the axiom) unless shown essentially undecidable (halt) — the two are not
interchangeable.
