# RDL Canonical Core — Specification

**Status:** draft for review · **Date:** 2026-07-12 · **Governs:** decomposition of the
`research-development-loop` monolith into a canonical core + modules + one leverage mechanism +
adaptive skill dispatch.

Principle (from the user): **R&D reduces degrees of freedom.** The core is defined to make every
construct a DOF-reducer; anything that adds a free variable without eliminating one is a defect.

## 1. State — a constraint system

The loop state is `S = (V, C)`:
- `V` = variables — open propositions and unbound design decisions.
- `C` = constraints — equations/inequalities from the manifest, the user, and gathered evidence.
- Residual sets are the solver's working memory: `K` = solved variables, `Q` = free variables,
  `E` = pruned values, `D` = elimination order, **gap** = an underdetermined variable
  (`⊬P ∧ ⊬¬P`), **glut** = an inconsistency (`⊢P ∧ ⊢¬P`).

`F(S)` = degrees of freedom = number of free variables = `|V| − rank(C)`.

## 2. Invariant (I) — monotone DOF reduction

Every step MUST reduce degrees of freedom, tighten toward an optimum, or classify. Concretely one
of: (a) eliminate a free variable (`ΔF ≤ 0`); (b) for an **inequality** system, *activate* a
constraint — move toward the feasible region's boundary/vertex (the base case where an inequality
becomes an equality); or (c) emit a `T`-classification, **including recognizing essential
undecidability** (a valid terminal, not a DOF increase). A step that introduces a free variable —
unbounded prose, an ad-hoc exception, an unenforced choice, a hedge — without doing one of (a)–(c)
is a **defect**, not a deliverable.

## 3. Terminal classification (T) — the only legal halts

`S` is a system of **equations and inequalities**. The loop halts iff it classifies `S` as
**exactly one** of the following. (Grounding: linear algebra for equalities; LP/convex duality for
inequalities; Gödel independence and MRDP/Hilbert's 10th for the undecidable cases.)

| Class | Condition | Emit |
|---|---|---|
| **DETERMINED** | equality system, `rank(C) = |V|` | the unique solution → deliver |
| **FEASIBLE (optimizable)** | inequality system, region non-empty | reduce to the base case — solve the active-constraint (equality) boundaries; the optimum is at a vertex where inequalities are tight. Deliver the optimum + the **binding** constraints. Not abdication. |
| **INFEASIBLE / INCONSISTENT** | empty region / glut (`rank[C] < rank[C|b]`) | the contradicting constraint pair + the rejected axiom |
| **UNDECIDABLE — non-essential** (a *gap*, `⊬P ∧ ⊬¬P`) | propositionally independent of current axioms; decidable in an extension | the **exact missing axiom** (observation/constraint/user input); the R&D action is to add it and re-solve |
| **UNDECIDABLE — essential** | undecidable in the theory *and every consistent extension* | name it and **halt** — no added observation decides it; further effort is provably wasted |

There are no other terminal states. "Done", "deferred", "logged skip", "N1…N4" are **not**
terminal states — each maps to a row above or is a defect. An "exception" is admissible only as
the *non-essential-undecidable* row, with its missing axiom named. A gap MUST be discharged as
non-essential (add the axiom) unless shown essentially undecidable (halt) — the two are not
interchangeable.

## 4. Phase model (κ) — formal DOF-reducers

A **phase** `κ` is a contract `⟨pre, reduction, post, accept⟩`:
`κ : (S, W) → (S′, W′)` over a target free-variable set `W`, where `post ⇒ (|W′| < |W|)` or a
`T`-classification, and `accept` is a mechanically checkable postcondition. (A phase is *not* a
capability. A **capability** is a tool / skill / dependency / permission / resource that is
`granted ∩ present`; a phase is carried out by binding it to a capable skill — see §5.)

Canonical phases (one module each):

| κ | Reduction it performs | accept (checkable) |
|---|---|---|
| `research` | isolate variables; add independent constraints; rank the system | residual with every `K` truth-typed + scoped; each `Q` has a named missing equation |
| `design` | elicit → canonical spec (EARS/RFC 2119/C4/MADR) | spec passes notation check; ≥2-alternative gates only when ≥2 exist |
| `plan` | WBS + Requirements Traceability Matrix; one SHALL→one test→one task | every task cites an existing `AC-n`; every task has a failing-test-first step |
| `develop` | TDD: RED (verified-failing) → GREEN (minimal) → REFACTOR | no production line without a prior failing test in the transcript |
| `isolate-root-cause` | reproduce → **one** hypothesis, one variable → fix; ≥3 failed ⇒ question the model | a failing regression test exists before any fix; no stacked fixes |
| `verify` | Definition of Done + V&V on fresh evidence | every claim backed by a command run in *this* pass; zero collection errors/warnings |
| `author-skill` | Agent Skills format + behavioral eval | frontmatter lints (whitelist keys, no `<>`); trigger/quality eval run, not just structural lint |
| `integrate` | GitHub Flow + Conventional Commits | prereqs met; commit type valid; write scope respected |

## 5. Adaptive dispatch (D) — open-ended, not hardcoded

For each phase `κ`, bind at runtime to the **best available** capable skill whose contract matches,
discovered from the (open-ended) available-skills set. Precedence:

```
most-specific available skill  ≻  the RDL's own fallback method for the phase  ≻  prompt (UNDERDETERMINED: name the missing capability)
```

No provider is hardcoded. `superpowers:<x>`, when present, is one admissible binding of the
matching phase — never a dependency, never forbidden. The loop **uses what is installed** and
falls back to its own method only when nothing capable is present; it never forbids a skill that
may or may not be installed. Binding MUST be recorded (which capability satisfied which phase) so
the run is reproducible.

## 6. Leverage mechanism (H) — one hook

A single `SessionStart`-class hook injects **this core** (I, T, D, and the phase index) into
context, so the governing contract is always present — the one mechanical primitive, carrying a
*formal contract* rather than prose discipline. (Superpowers gets its leverage from one injection
hook; we inject a formalism, not exhortation.)

## 7. Module decomposition (what the monolith becomes)

```
research-development-loop/
  SKILL.md                 # thin orchestrator: I, T, D, phase index, links only
  core/
    invariant.md           # §2 I
    terminal.md            # §3 T
    dispatch.md            # §5 D + binding record format
  phases/
    research.md design.md plan.md develop.md
    isolate-root-cause.md verify.md author-skill.md integrate.md   # §4, one κ per file
  hooks/rdl-core.json      # §6 H (SessionStart injection of the core)
  references/…             # existing manifest.md etc.
  scripts/lint_skill.py    # existing; extended per author-skill.accept
```

Each `phases/<κ>.md` states only: contract, the method, and the checkable `accept`. The
orchestrator holds no per-phase procedure — it holds I, T, and D plus global governance.

## Open (UNDERDETERMINED — the missing equations, for the reviewer)

- U1: phase set — is the §4 basis complete/minimal, or add/remove a `κ`?
- U2: hook packaging — a skill chain cannot self-install a `SessionStart` hook; H ships as a
  `hooks/rdl-core.json` + a documented `settings.json` merge (user applies), or via `update-config`.
  Which delivery? (This is the one variable I cannot pin without you.)
