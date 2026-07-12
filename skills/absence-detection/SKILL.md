---
name: absence-detection
description: Use when evaluating any capability claim for silent failure modes — conditions where an implementation fails without raising a test exception or triggering a hook event. Apply before declaring a test suite clean, before finalizing a scholarly review, or whenever you need to know what a test battery cannot see. Invoke this skill for any claim of the form "the implementation handles X" to surface what is structurally invisible to event-driven testing.
---

# Absence Detection

## Core Principle

Tests and hooks are event-driven: they fire on things that happen. They are structurally blind to things that **don't** happen — failures that produce wrong output without raising an exception, failure modes that kill the process before any hook fires, and capabilities that were never exercised under the conditions that matter.

**Absence detection is the in-model mechanism for capturing what event-driven systems cannot see.**

## When to Use

- Evaluating a capability claim ("this implementation handles X") before declaring it verified
- Finalizing a scholarly paper or research residual — the N category requires this analysis
- After running a test suite — to reason about what the suite does NOT cover
- Before handing off code to a dependent implementation or successor agent
- Whenever the question is "what is missing?" rather than "what was found?"

## The Method: Reject(P) Analysis

For each capability claim P:

**Step 1 — State P precisely.** A vague P produces vague absences. "The implementation handles X" is better stated as "when condition C holds, function F produces output O without side-effect S."

**Step 2 — Apply Reject(P).** Ask: which premises, axioms, or environmental conditions would have to be FALSE for P to fail? Not "what could go wrong in general" — specifically: what load-bearing assumptions does P rest on?

Enumerate each assumption:
- Which inputs does P assume are well-formed?
- Which external services or resources does P assume are available?
- Which invariants in the surrounding system does P depend on?
- Which execution context assumptions does P make (environment variables, file paths, network, concurrency model)?

**Step 3 — Classify each falsified assumption by detectability.**

| Detectability | Meaning | Examples |
|---------------|---------|---------|
| **Survivable / test-visible** | Failure raises an exception that tests catch | `ValueError`, `FileNotFoundError`, assertion error |
| **Survivable / silent** | Failure produces wrong output without raising | Wrong numeric result, silent truncation, swapped field values |
| **Unsurvivable** | Failure kills the process before any hook fires | OOM kill, SIGKILL, parent process crash |

Only survivable/test-visible failures are detectable by a test suite. The other two require absence tracking.

**Step 4 — Produce N entries** for every silent or unsurvivable failure mode found:

```
N1: {capability or condition} — confirmed absent: {reason / how confirmed}
N2: {condition} — unsurvivable: {why hooks or tests cannot detect this failure}
N3: {capability} — silent wrong output: {what wrong output looks like, why no exception is raised}
```

N entries go into the N category of the research residual, or into the mandatory negative inventory section of a scholarly paper.

## Worked Example

**Claim P:** "The graph builder handles disconnected graphs correctly."

**Reject(P) — what would have to be false:**
1. The eigensolver must converge on a disconnected Laplacian (assumption: well-conditioned matrix)
2. The output must be deterministic across runs (assumption: eigensolver is numerically stable)
3. Seeds must be present in the graph (assumption: non-empty seed set)

**Classify:**
- Assumption 1 fails → eigensolver returns wrong eigenvalues silently (no exception) → **N entry: silent wrong output**
- Assumption 2 fails → eigsh numerical non-determinism → **N entry: silent wrong output**
- Assumption 3 fails → `NodeNotFound` before any guard fires → **N entry: survivable but test-visible only if tested**; if no test covers empty seeds → **N entry: confirmed absent from coverage**

**Output N entries:**
```
N1: disconnected-graph eigensolver correctness — silent wrong output: eigsh may return incorrect eigenvalues on rank-deficient Laplacians without raising; no test covers disconnected input
N2: eigensolver numerical determinism — unsurvivable awareness: eigsh result differs run-to-run on near-zero eigenvalues; test suite uses a single-run assertion, so non-determinism passes silently
N3: empty seed set — confirmed absent: no test exercises seed={}, exception path depends on NodeNotFound not NetworkXError (the existing guard is ineffective)
```

## Relationship to Research Residual

Reject(P) analysis is the primary source of N entries in the K/Q/C/E/D/A/N residual format. Run absence detection:
- At Phase 0 Step 0.7 (proposition evaluation) for any capability claim in the residual
- At Phase 5 (scholarly review) to produce the mandatory negative inventory

The N entries produced here flow directly into the negative inventory section of the paper. The negative inventory is not a post-hoc addition — it is built from N entries accumulated during research, not invented at review time.

## What Absence Detection Is NOT

- **Not pessimism:** Absence detection does not claim the implementation is wrong. It identifies conditions that CANNOT BE CONFIRMED by the test suite.
- **Not duplicate of Q entries:** Q entries are open questions (insufficient evidence either way). N entries are confirmed absences (confirmed by structural analysis of the test suite's detection surface).
- **Not optional:** A scholarly review or research residual that omits the N category has not completed this analysis. Passing tests confirm survivable behaviors under tested conditions — nothing more.
