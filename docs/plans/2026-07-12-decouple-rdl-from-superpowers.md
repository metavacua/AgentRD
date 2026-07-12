# Plan — Decouple the RDL skill chain from `superpowers`

**Date:** 2026-07-12 · **Manifest:** `rdloop.toml` (docs_dir=`docs`, vcs=`git`) ·
**Decisions (user-approved):** (1) *Inline standard + credit* — remove `superpowers:` as a
hard runtime dependency; the loop MUST run to completion with the superpowers plugin absent;
credit it as a compatible reference implementation. (2) *Agent Skills spec + linter* — replace
`superpowers:writing-skills` / `skill-creator` with the Agent Skills open format + a JSON-Schema
frontmatter validator + lint script.

## Global Constraints (RFC 2119 / BCP 14)

- **GC-1** The RDL loop MUST NOT invoke any `superpowers:<skill>` as a *required* step. Every
  such invocation MUST be replaced by an inlined, industry-standard method.
- **GC-2** Each replaced method MUST cite a verified industry standard (see mapping) and MAY
  credit the superpowers original as a "compatible reference implementation."
- **GC-3** The `superpowers` string MAY remain ONLY in reference-implementation credits, never
  as an invocation. (Guardrail: `test_no_hard_superpowers_invocation`.)
- **GC-4** The base manifest default `docs_dir` MUST be `docs`, not `docs/superpowers`.
- **GC-5** All 6 chain skills MUST pass the new Agent Skills frontmatter linter.
- **GC-6** The existing 54 tests plus the `test_agnostic_*` guardrails MUST stay green.

## Industry-standard mapping (all verified 2026-07-12)

| superpowers dep | replacement | standard |
|---|---|---|
| brainstorming process | structured requirements elicitation + design-review gate | ISO/IEC/IEEE 29148; EARS; RFC 2119 |
| writing-plans structure | WBS + Requirements Traceability Matrix + TDD | 29148 (RTM); Beck TDD |
| systematic-debugging | Root-Cause Analysis + regression test | ASQ RCA (5 Whys / Ishikawa) |
| verification-before-completion | Definition of Done + V&V | Scrum DoD; IEEE 1012 |
| finishing-a-development-branch | GitHub Flow + Conventional Commits | GitHub Flow; ConvCommits 1.0.0 |
| writing-skills / skill-creator | Agent Skills format + schema lint | agentskills.io spec |
| subagent-driven-development | manifest `[delegation]` (already agnostic) | — |

## Tasks (each: failing test → run/fail → implement → run/pass)

- **T1 — Skill frontmatter linter (the recursive-dep substitute).**
  Files: `research-development-loop/scripts/lint_skill.py`,
  `research-development-loop/references/skill-frontmatter.schema.json`,
  `research-development-loop/tests/test_lint_skill.py`.
  AC: valid skill passes; bad `name` (leading/trailing/consecutive hyphen, uppercase, >64) fails;
  `description` missing or >1024 fails; missing frontmatter fails; all 6 chain skills pass.
  Satisfies GC-5. Std: Agent Skills format (K9).

- **T2 — De-invoke the orchestrator.** File: `research-development-loop/SKILL.md`.
  Replace each `superpowers:X` invocation with the mapped inline method + credit; replace
  `docs/superpowers/{plans,specs}` with `{[project].docs_dir}/...`. Add a "Reference
  implementations" credit note. Satisfies GC-1..GC-3.

- **T3 — Inline the brainstorming process.** File: `rdl-brainstorming/SKILL.md`.
  Spell out the process (explore context; one question at a time; 2-3 approaches; approval gates;
  self-review; user gate) inline; credit superpowers as reference. Update description line.

- **T4 — Inline the plan structure.** File: `rdl-writing-plans/SKILL.md`.
  Spell out the plan template (header; Global Constraints; Task N Files/Interfaces; TDD checkbox
  steps; no placeholders) inline, framed as WBS+RTM+TDD; credit superpowers.

- **T5 — Path-decouple research-phase + references.** Files: `research-phase/SKILL.md`,
  `research-development-loop/references/issue-governance.md`,
  `research-development-loop/references/example-manifest.metavacua.toml`.
  Replace `docs/superpowers/...` with `{[project].docs_dir}/...`.

- **T6 — Base-manifest default.** Files: `research-development-loop/rdloop/schema.py`
  (BASE_MANIFEST), `research-development-loop/rdloop/rdloop.base.toml`,
  `research-development-loop/tests/test_manifest.py` (assert docs_dir default == `docs`).
  Satisfies GC-4.

- **T7 — Rewire the coupling tests.** File: `rdl-brainstorming/tests/test_rdl_rewired.py`.
  Replace `test_superpowers_process_still_credited` intent: assert (a) no hard `superpowers:`
  *invocation* in the chain, (b) superpowers still *credited*. Add
  `test_no_hard_superpowers_invocation` across orchestrator + sub-skills. Satisfies GC-3.

- **T8 — Evals.** File: `research-development-loop/evals/evals.json`.
  Update the `anomaly-routes-to-systematic-debugging` eval to reflect RCA-first (keep intent);
  ensure no eval requires invoking the superpowers plugin.

- **T9 — Verify (Phase 4).** Full `pytest skills/` green; grep proves no `superpowers:` invocation
  remains (only credits); linter passes on all 6 skills. Definition of Done met.
