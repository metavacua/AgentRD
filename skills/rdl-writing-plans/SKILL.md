---
name: rdl-writing-plans
description: RDL Phase 2 planning skill. Produces a TDD implementation plan from an rdl-brainstorming design doc, inheriting the superpowers writing-plans structure (bite-sized tasks, exact paths, Interfaces, no placeholders) and adding RFC 2119 Global Constraints and AC->task->test traceability.
---

# RDL Writing Plans (Traceable TDD Plans)

Follow the superpowers writing-plans *structure* verbatim (header; Global Constraints; Task N
with Files/Interfaces; bite-sized checkbox steps: write failing test → run/fail → implement →
run/pass → commit; no placeholders; self-review). This skill adds two things.

**Announce at start:** "Using rdl-writing-plans to produce a traceable TDD plan."

Write to `{[project].docs_dir}/plans/YYYY-MM-DD-<topic>.md`. Commit only if `[project].vcs = "git"`.

## Addition 1 — RFC 2119 Global Constraints
Write the Global Constraints section using RFC 2119 keywords (ALL-CAPS = normative). Copy the
design doc's `MUST`/`SHOULD`/`MAY` constraints verbatim.

## Addition 2 — AC→task→test traceability
Every task MUST cite the `AC-n` acceptance criterion it satisfies and the `ADR-n` decision that
justifies it. The task's failing-test step MUST assert that AC's `SHALL` clause. One `SHALL` →
one test → one task. Validate citations with `rdl-brainstorming/scripts/check_notation.py`
(`plan_task_cites_ac`): every cited `AC-n` MUST exist in the design doc (no dangling references).
