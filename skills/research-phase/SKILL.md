---
name: research-phase
description: Use at the start of any non-trivial development task to build a complete picture before design decisions are made. Produces a structured research residual (K/Q/C/E/D/A/N format) by running a series of tool calls and proposition evaluation steps. Invoke from the research-development-loop skill at Phase 0, or directly whenever you need a systematic evidence base before committing to an approach. Also callable as a micro-cycle (steps 0.1+0.2+0.7 only) when any downstream phase encounters an unresolved gap or glut.
---

# Research Phase

Produces a research residual by running a structured series of steps. The steps alternate between deterministic tool calls (date, git, gh, grep) and non-deterministic reasoning (scope assessment, proposition evaluation). The residual is the canonical knowledge state for all downstream work.

## Step 0.0 — Scope the task

Answer these four questions before running any other step:

1. Is this task **fully local**? (No external API, no GitHub issues, no web docs needed)
2. Is this task **fully specified**? (No design ambiguity, no unknown constraints)
3. Is this task **mechanically bounded**? (Rename, refactor, boilerplate — no new architecture)
4. Is this task **self-contained**? (No dependency on parallel task output)

If **all four YES** → **mechanical task**: run only steps 0.1 and 0.3, emit a minimal residual with K entries only, skip steps 0.2/0.4/0.5/0.6/0.7.

If **any NO** → **research-grade task**: run all steps 0.1–0.8.

## Step 0.1 — Ground the current date

```bash
date +%Y-%m-%d
```

Record the date. Use it in all web searches and API queries. Treating cached knowledge as current is a research failure.

## Step 0.2 — Web search for current state

Run `WebSearch` for:
- Current documentation for every external tool, API, or library the task touches
- Relevant GitHub issues, changelogs, breaking changes since last known state
- Current-year best practices for the approach under consideration

If the topic is unfamiliar or a version change is suspected, spawn a research subagent rather than relying on training-data recall.

## Step 0.3 — Read current codebase state

```bash
# Gated on [project].vcs. If vcs="none": SKIP git context (log the skip), read files directly.
git branch --show-current   # only if vcs="git"
git status                  # only if vcs="git"
git log --oneline -15       # only if vcs="git"
# Open PRs: only if issues.tracker != "none" AND "gh" is in [capabilities].subprocess,
# iterating [issues].read_repos. Ungranted → logged skip.
```

Read relevant specs (`{[project].docs_dir}/specs/`) and plans (`{[project].docs_dir}/plans/`).

## Step 0.4 — Check issue tracker

Only if `[issues].tracker != "none"` and `gh` is granted in `[capabilities].subprocess`.
Iterate `[issues].read_repos`; for each repo run `gh issue list --repo <repo> --state open`.
If the tracker is `none` or `gh` is ungranted, this step is **non-critical → logged skip**
("skipped issue check: no tracker/gh grant"), not a silent no-op.

Search for existing reports of the task, blocked predecessors, and related work before proposing anything new.

## Step 0.5 — Dependency analysis

Map dependency direction before making sequencing decisions.

**Task-level:** for each pair of candidate tasks (A, B): does A produce something B consumes? If yes, A → B.

**Package/library-level:**

```bash
# Full SBOM with versions and licenses
gh api /repos/{owner}/{repo}/dependency-graph/sbom | python3 -m json.tool | less
# Dependency diff between commits
gh api /repos/{owner}/{repo}/dependency-graph/compare/main...HEAD
# Known vulnerabilities
gh api /repos/{owner}/{repo}/dependabot/alerts
```

Local commands when GitHub graph is unavailable or transitive depth is needed:

Run only the toolchains present in `[capabilities].subprocess`. A toolchain absent from
the grants is **non-critical → logged skip** for that ecosystem ("skipped npm checks:
npm not granted") — never a silent "no dependencies found" (which would be a false-clean).

| Ecosystem | Command |
|-----------|---------|
| Python | `uv pip tree` or `pipdeptree`; `pip show <pkg>`; `poetry show --tree` |
| JavaScript | `npm ls --all`; `npm why <pkg>`; `yarn why <pkg>` |
| Go | `go mod graph`; `go mod why <module>`; `go list -m all` |
| Rust | `cargo tree`; `cargo tree --duplicates` |
| Bash | `grep -rn '^source\|^\. ' --include="*.sh" .` |

**Test environment check** (mandatory for projects with a test suite):

```bash
cat pyproject.toml | grep -A5 '\[tool.pytest'   # identify canonical runner
cat Makefile 2>/dev/null | grep -E 'test|pytest'
uv pip list 2>/dev/null          # uv-managed env
python3 -m pip list 2>/dev/null  # system python (may differ)
```

Declared ≠ installed. Running the wrong test runner silently skips entire test files.

**Codebase structural:**

```bash
grep -r "^import\|^from" --include="*.py"
```

Or use `scripts/github_graph.py` / `scripts/extract-graph.py` for an explicit N-Triples dependency graph.

**Ordering rule:** if A → B at any level, do A first. If independent at all levels, treat as parallelizable.

## Step 0.6 — Query graph context

If a graph-context capability is declared under `[x].graph_context` and its scripts are
granted in `[capabilities].subprocess`, query the graph. Otherwise this step is
**non-critical → logged skip**.

## Step 0.7 — Proposition evaluation

Collect every key claim, hypothesis, or design choice surfaced by steps 0.1–0.6. For each proposition P, evaluate in both directions:

**Accept(P):** what must also be true if P holds? What behaviors, constraints, or obligations follow necessarily?

**Reject(P):** which premises, axioms, or assumptions would have to be false for P to fail? These are the load-bearing foundations.

For each hypothesis, classify:
- **Gap** (⊬ P and ⊬ ¬P): insufficient evidence — add Q entry, trigger a micro-cycle web search
- **Glut** (⊢ P and ⊢ ¬P from distinct streams): formal inconsistency — identify which stream is defeasible; expose the contradicted axiom as an E entry or new Q entry; do NOT compress

**Epistemic classification — required for every K entry.** Before labelling any fact as K, assign it one of four truth-types and append the tag in brackets:

| Tag | Meaning | Permitted source |
|-----|---------|-----------------|
| `[empirical]` | Observed or measured in this session; deterministic tool output or primary-source read | `date`, `git`, `gh`, file read, benchmark output |
| `[verified]` | Checked against an authoritative reference in this session | Court opinion text, official spec, primary source fetched now |
| `[sound: from K_n, K_m]` | Valid argument from premises that are themselves `[empirical]` or `[verified]`; cite the premises | Both premises confirmed; conclusion follows necessarily |
| `[valid: from K_n]` | Logically follows from the cited K entry, but that premise is not yet `[empirical]` or `[verified]` | Interim step in a chain; treat the chain as Q until the root premise is confirmed |

**Banned from K entries: `[training-recall]`.** Any claim whose only support is the model's training-data memory — not independently confirmed in this session by a tool call, file read, or cited source fetch — is NOT a K entry. Put it in Q. Mark it "(unverified: training-recall)" in the Q entry. Prefer a gap over false certainty.

**Scope-adequacy tag — required alongside every K entry's truth-type.** A claim can be perfectly true, properly epistemically tagged, and still function as a false answer once used to resolve a broader proposition than the one it actually covers. Adversarial verification (including subagent-based fan-out research) checks whether a claim is *accurate* — it does not check whether the claim is *adequate to the scope of the question it's being deployed to answer*. A narrow-but-true sub-claim surviving a 3-vote confirm does not mean the broader proposition is settled.

Every K entry therefore carries a second required bracket, immediately after the truth-type tag: `[scope: full]` or `[scope: partial — {what's excluded}; see Q{n}]`.

- `[scope: full]` — the claim, as stated, fully resolves the proposition it's answering. Use this only after checking: does this claim's own subject matter (not just its truth) match the calling question's subject matter, or only a narrower slice of it?
- `[scope: partial — ...]` — the claim is true but covers less ground than the question asks. It MUST be paired with a Q entry carrying the unaddressed remainder. A `[scope: partial]` K entry is never sufficient on its own to close out the proposition it was raised to answer.

**Worked example of the failure this catches** (real case, not hypothetical): the question "is `wasm32-unknown-unknown` useful for compile-time capability gating?" was answered with a rustc-docs-sourced, 3-0-adversarially-confirmed claim that "`std::fs` and `std::thread::spawn` compile but stub to a runtime error on this target, not a compile failure." That claim is true and was properly tagged `[verified]` — but its actual subject is *`std`'s own facade*, a narrower thing than "compile-time gating on this target" as a whole. Tagged honestly, it would have read `[verified] [scope: partial — covers std's own API surface only; does not address third-party crate/feature-gate compile failures, which is the practically dominant gating mechanism]`, with a paired Q entry. Instead it stood alone as if settled, and was only caught when the user pointed to their own repo's CI (a real, disciplined Cargo-feature-gating setup that does compile-time-gate hardware-specific code on that exact target) as a direct counterexample to the unscoped claim. **The rule that would have caught this before deployment:** before tagging any K entry `[scope: full]`, name the calling proposition's subject in one clause and check the claim's own subject against it word-for-word — if the claim's subject is a proper subset (e.g. "std's facade" vs. "this target's gating capability as a whole"), it is `[scope: partial]`, no exceptions for how strongly the narrower claim was verified.

**A second flavor of the same failure:** scope mismatch isn't only "narrower slice of the same subject" — it also covers *substituting a weaker or adjacent analog for a more precise source that a different search angle might have found*, without disclosing the substitution. (Real case, same session: a question asking for the canonical source grounding a specific three-part distinction was answered with a type-theory analog found via CS/programming-language-theory search angles — a reasonable finding, but the search never queried mathematical-logic angles directly, where a more precise, more established grounding existed. The analog should have been tagged `[scope: partial — closest match from the search angles run; a more direct source may exist in an unqueried field; see Q{n}]`, not presented as though the search had settled it.) The same word-for-word subject check catches this: if the claim's subject is "the closest thing this search found" rather than "the specific thing the question named," it is `[scope: partial]`.

**Bias rule — truth over falsity, truth over randomness:**
- A Q entry (acknowledged gap) is epistemically better than a K entry based on plausibility
- A `[valid: from K_n]` entry is epistemically weaker than `[sound: from K_n]`; label it honestly
- When the premise of a valid chain is itself only `[valid:]`, the whole chain is Q until grounded in `[empirical]` or `[verified]`
- Do not accumulate unverified claims into K to "fill out" the residual; an honest, sparse K is more useful than a dense K polluted with training-recall
- A `[scope: partial]` K entry is epistemically better than the same claim mislabeled `[scope: full]`; a narrow true claim standing in for a broad question is a silent failure no downstream test will catch, exactly like an unqualified K

**Absence detection:** For every capability claim, invoke the `absence-detection` skill to apply Reject(P) specifically for *silent failure modes* — conditions where P fails without producing a test exception or hook event. The N entries produced flow directly into the residual. This step is not optional when any claim of capability is in the residual.

## Step 0.8 — Residual output

Emit the residual in the conversation thread. The residual is a semantically compressed, non-redundant record of what cannot be trivially derived from the codebase on demand:

```
## Research Residual — {task-slug}

K (Known — verified, sourced; truth-type + scope required):
  K1: {fact} [source] [empirical] [scope: full]      ← tool output or primary source read this session
  K2: {fact} [source] [verified] [scope: full]       ← cross-checked against authoritative ref this session
  K3: {fact} [valid: from K1] [scope: full]          ← logically follows; premise may not be confirmed
  K4: {fact} [sound: from K1, K2] [scope: partial — {excluded}; see Q{n}]  ← true but narrower than the question it answers

Q (Open — unresolved, with bifurcated analysis):
  Q1: {question}
    Accept({P}) → consequences: {what follows}
    Reject({P}) → exposed premise: {axiom that would have to be false}
  Q2 (scope remainder of K4): {the excluded part K4 didn't cover} — unresolved, not silently dropped

C (Constraints — hard limits on any solution):
  C1: {constraint}

E (Eliminated — rejected hypotheses with causal axiom):
  E1: {hypothesis} — rejected: axiom {X} is false; evidence: {source}

D (Dependencies — task execution order):
  {A} → {B}: {reason}
  {C} ∥ {D}: independent (no shared inputs/outputs)

A (Artifacts — non-propositional verbatim content):
  A1: {type} {description}
  {verbatim content — code snippet, schema, proof trace, config fragment}

N (Negatives — confirmed absences, untested conditions, unsurvivable failure modes):
  N1: {capability or condition} — confirmed absent: {reason / how confirmed}
  N2: {condition} — unsurvivable: {why hooks or tests cannot detect this}
```

**K vs A:** K entries are propositional facts. A entries are verbatim, non-propositional content that downstream phases need intact — a code snippet, API response, config schema. If a sentence describes it completely → K. If the downstream phase needs it verbatim → A.

Any downstream phase can request elaboration of a specific entry without re-reading the full residual.

---

## Micro-Cycle Mode

When any downstream phase (brainstorm, planning, development, verification) encounters an unresolved gap or glut, invoke this skill in micro-cycle mode:

1. Package the issue as a new Q entry with P and blank Accept/Reject fields
2. Run step 0.1 (verify date current), step 0.2 (targeted web search for the specific question), step 0.7 (proposition evaluation for this Q entry only)
3. Update the residual in-place — fill the Q entry, promote to K or E if conclusive
4. Return the updated Q (or K/E) to the calling phase

The residual is the canonical state throughout the loop. All phases read from and write to it.
