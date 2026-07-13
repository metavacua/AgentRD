---
name: rdl-writing-plans
description: RDL Phase 2 planning skill. Produces a TDD implementation plan from an rdl-brainstorming design doc using a self-contained Work-Breakdown-Structure + Requirements-Traceability-Matrix template (bite-sized tasks, exact paths, Interfaces, no placeholders) and adding RFC 2119 Global Constraints and AC->task->test traceability.
---

# RDL Writing Plans (Traceable TDD Plans)

Use this self-contained plan *structure* — a **Work-Breakdown Structure** whose leaves are
TDD-driven tasks, each traced through a **Requirements Traceability Matrix** (ISO/IEC/IEEE 29148):

- **Header** — title, date, manifest reference, source design doc.
- **Global Constraints** — RFC 2119 (see Addition 1).
- **Task N** — a **Files** list (exact paths, no placeholders) and an **Interfaces** block
  (exact signatures/schemas the task must satisfy).
- **Bite-sized checkbox steps** per task: write failing test → run/fail → implement → run/pass →
  commit. No placeholders, no "TBD".
- **Self-review** — check every task has a failing-test-first step and a real AC citation.

(The Superpowers `superpowers:writing-plans` skill is a compatible reference implementation of
this structure and MAY be used interchangeably where present; it is not required.) This skill
adds two things.

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
