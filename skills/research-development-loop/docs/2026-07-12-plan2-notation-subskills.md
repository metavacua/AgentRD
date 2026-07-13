> **Historical record (superseded).** This dated plan documents work completed *before* the `superpowers` decoupling of 2026-07-12. Its `superpowers` references are preserved as a record, not current guidance. Current design: `docs/plans/2026-07-12-decouple-rdl-from-superpowers.md`.

# Plan 2 (D-B) — RDL Notation Subskills (`rdl-brainstorming`, `rdl-writing-plans`) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create two RDL-owned local skills that produce industry-standard structured specs — EARS acceptance criteria, RFC 2119 constraints, MADR decisions, arc42-lite structure, a Structurizr-DSL-only architecture model, a paraconsistent glut register, and AC→task→test traceability — with a Rice-correct content-gated notation valve.

**Architecture:** A pure-Python validator (`rdl-brainstorming/scripts/check_notation.py`, stdlib `re` only) encodes every machine-checkable rule (EARS pattern classification, RFC 2119 all-caps detection, content-gating thresholds, Structurizr skip-logging, AC citation). Two `SKILL.md` files carry the process prose and reference the validator. The superpowers plugin is untouched; RDL Phases 1/2 are rewired to invoke these.

**Tech Stack:** Python 3.11 (`re` stdlib), pytest 7.2, Markdown SKILL files, Structurizr DSL (text; render deferred when ungranted).

## Global Constraints

- **C-NOTRIVIA:** no auto-decided triviality; default non-trivial; EARS+RFC 2119 universal; expensive sections gated on decidable structural presence (element/alternative counts).
- **C-GLUT:** design docs carry a first-class glut register; contradictions recorded, never silently reconciled.
- **C-COBC:** architecture diagrams are correct-by-construction views derived from a single Structurizr `.dsl` model. Structurizr DSL only — no RDF/OWL architecture layer.
- **C-SPINE:** document metadata uses Dublin Core + Schema.org (shared with Phase 5 scholarly-white-paper).
- **C-UNTOUCHED:** never edit the superpowers plugin; new behavior lives in `~/.claude/skills/rdl-*`.
- **Toolchain gating:** structurizr is an OPTIONAL dependency. Always write the `.dsl` text source; render/validate only if structurizr is USABLE (granted ∧ present — Plan-1 `schema.usable`), else log a skip naming the disabled feature (`architecture-rendering`). Never a silent no-op.
- **vcs=none here:** every "Commit" step is a logged no-op.
- **Depends on Plan 1** for the manifest (`schema.gate`, `[project].docs_dir`, `[capabilities].subprocess`).
- **Paths:** `BRAIN/` = `/home/metavacua/.claude/skills/rdl-brainstorming/`; `PLANW/` = `/home/metavacua/.claude/skills/rdl-writing-plans/`; `RDL/` = `/home/metavacua/.claude/skills/research-development-loop/`.

---

### Task 1: Notation validator core

**Files:**
- Create: `BRAIN/scripts/__init__.py` (empty), `BRAIN/scripts/check_notation.py`
- Test: `BRAIN/tests/test_notation.py`

**Interfaces:**
- Produces: `classify_ears(clause) -> str|None` (one of `event|state|unwanted|optional|ubiquitous`); `is_ears(clause) -> bool`; `normative_keywords(text) -> list[str]` (ALL-CAPS RFC 2119 only); `arch_section_required(element_count:int) -> bool`; `adr_required(alt_count:int) -> bool`; `structurizr_action(usable_structurizr: bool) -> str` (`"render"` | `"skip:architecture-rendering-disabled"`; usability = granted ∧ present via Plan-1 `schema.usable`); `plan_task_cites_ac(task_text, valid_acs) -> bool`.

- [ ] **Step 1: Write the failing tests**

```python
# BRAIN/tests/test_notation.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import check_notation as n

def test_ears_five_patterns():
    assert n.classify_ears("WHEN mute is selected THE laptop SHALL suppress audio") == "event"
    assert n.classify_ears("WHILE no card is present THE ATM SHALL display insert-card") == "state"
    assert n.classify_ears("IF the input is invalid THEN THE system SHALL reject it") == "unwanted"
    assert n.classify_ears("WHERE a GPU is fitted THE renderer SHALL enable SIMD") == "optional"
    assert n.classify_ears("THE service SHALL log every request") == "ubiquitous"

def test_ears_rejects_non_ears():
    assert n.classify_ears("the system should probably log stuff") is None
    assert n.is_ears("THE x SHALL y") is True
    assert n.is_ears("please make it fast") is False

def test_rfc2119_only_allcaps_is_normative():
    kws = n.normative_keywords("The system MUST retry but should not block")
    assert "MUST" in kws
    assert "SHOULD NOT" not in kws  # lowercase 'should not' is informal (RFC 8174)

def test_content_gating_thresholds():
    assert n.arch_section_required(1) is False
    assert n.arch_section_required(2) is True
    assert n.adr_required(1) is False
    assert n.adr_required(2) is True

def test_structurizr_action_gated():
    assert n.structurizr_action(True) == "render"                       # usable = granted ∧ present
    assert n.structurizr_action(False) == "skip:architecture-rendering-disabled"  # optional-dep skip names the feature

def test_plan_task_cites_live_ac():
    assert n.plan_task_cites_ac("implements AC-3 per ADR-1", ["AC-1", "AC-3"]) is True
    assert n.plan_task_cites_ac("implements AC-9", ["AC-1", "AC-3"]) is False  # dangling ref
    assert n.plan_task_cites_ac("no citation here", ["AC-1"]) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BRAIN && python3 -m pytest tests/test_notation.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts'`

- [ ] **Step 3: Create `scripts/__init__.py`** (empty file).

- [ ] **Step 4: Write the validator**

```python
# BRAIN/scripts/check_notation.py — machine-checkable notation rules.
import re

EARS = {
    "event":      re.compile(r"\bWHEN\b.+\bTHE\b.+\bSHALL\b", re.S),
    "state":      re.compile(r"\bWHILE\b.+\bTHE\b.+\bSHALL\b", re.S),
    "unwanted":   re.compile(r"\bIF\b.+\bTHEN\b.+\bSHALL\b", re.S),
    "optional":   re.compile(r"\bWHERE\b.+\bTHE\b.+\bSHALL\b", re.S),
    "ubiquitous": re.compile(r"\bTHE\b.+\bSHALL\b", re.S),
}
# Keyword-led patterns are checked before the catch-all ubiquitous pattern.
_ORDER = ("event", "state", "unwanted", "optional", "ubiquitous")

def classify_ears(clause: str):
    """Return the EARS pattern name for `clause`, or None if it is not EARS."""
    for name in _ORDER:
        if EARS[name].search(clause):
            return name
    return None

def is_ears(clause: str) -> bool:
    return classify_ears(clause) is not None

RFC2119 = ["MUST NOT", "MUST", "SHALL NOT", "SHALL", "SHOULD NOT", "SHOULD",
           "REQUIRED", "RECOMMENDED", "MAY", "OPTIONAL"]

def normative_keywords(text: str):
    """Return RFC 2119 keywords that appear in ALL-CAPS (normative per RFC 8174)."""
    found = []
    for kw in RFC2119:
        # case-sensitive: uppercase kw only matches uppercase in text
        if re.search(r"(?<![A-Za-z])" + re.escape(kw) + r"(?![A-Za-z])", text):
            found.append(kw)
    return found

def arch_section_required(element_count: int) -> bool:
    """Decidable content-gate: architecture/C4 view required iff >=2 model elements."""
    return element_count >= 2

def adr_required(alt_count: int) -> bool:
    """Decidable content-gate: an ADR record required iff a decision has >=2 alternatives."""
    return alt_count >= 2

def structurizr_action(usable_structurizr: bool) -> str:
    """Map usability (granted AND present — computed via Plan-1 schema.usable) to an action.
    'render' iff usable; else an OPTIONAL-dependency skip that names the disabled feature.
    Never a silent no-op; the .dsl source is authored either way."""
    return "render" if usable_structurizr else "skip:architecture-rendering-disabled"

def plan_task_cites_ac(task_text: str, valid_acs) -> bool:
    """True iff the task cites >=1 AC-n and every cited AC exists in valid_acs."""
    cited = set(re.findall(r"\bAC-\d+\b", task_text))
    return bool(cited) and cited.issubset(set(valid_acs))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BRAIN && python3 -m pytest tests/test_notation.py -q`
Expected: PASS (6 passed)

- [ ] **Step 6: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 2: `rdl-brainstorming` SKILL.md + notation reference

**Files:**
- Create: `BRAIN/SKILL.md`, `BRAIN/references/notation.md`
- Test: `BRAIN/tests/test_brain_skill.py`

**Interfaces:**
- Consumes: `scripts/check_notation.py` (Task 1), Plan-1 manifest keys (`[project].docs_dir`, `[capabilities].subprocess`).
- Produces: a skill whose design-doc structure includes the metadata spine, RFC 2119 constraints, EARS ACs, Structurizr model, MADR (gated), and glut register; declares the Rice-correct valve.

- [ ] **Step 1: Write the failing test**

```python
# BRAIN/tests/test_brain_skill.py
from pathlib import Path
BRAIN = Path("/home/metavacua/.claude/skills/rdl-brainstorming")

def test_frontmatter_name():
    text = (BRAIN / "SKILL.md").read_text()
    assert "name: rdl-brainstorming" in text

def test_declares_all_notation_sections():
    text = (BRAIN / "SKILL.md").read_text().lower()
    for token in ["dublin core", "schema.org", "rfc 2119", "ears", "structurizr", "madr", "glut register"]:
        assert token in text, f"SKILL.md missing '{token}'"

def test_valve_is_rice_correct():
    text = (BRAIN / "SKILL.md").read_text().lower()
    assert "non-trivial" in text and "content-gat" in text
    assert "must not" in text and "triviality" in text  # forbids auto-deciding triviality

def test_structurizr_only_no_rdf_architecture():
    text = (BRAIN / "SKILL.md").read_text().lower()
    assert "structurizr dsl only" in text

def test_notation_ref_lists_five_ears_patterns():
    text = (BRAIN / "references" / "notation.md").read_text().lower()
    for p in ["ubiquitous", "event-driven", "state-driven", "unwanted", "optional"]:
        assert p in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd BRAIN && python3 -m pytest tests/test_brain_skill.py -q`
Expected: FAIL — `FileNotFoundError` for `SKILL.md`

- [ ] **Step 3: Write `BRAIN/SKILL.md`**

```markdown
---
name: rdl-brainstorming
description: RDL Phase 1 design skill. Turns an idea into an industry-standard structured spec (Dublin Core + Schema.org metadata, RFC 2119 constraints, EARS acceptance criteria, Structurizr-DSL architecture model, MADR decisions, paraconsistent glut register) using a Rice-correct content-gated notation valve. Inherits the superpowers brainstorming process (one question at a time, 2-3 approaches, approval gates) and adds the notation layer to the output.
---

# RDL Brainstorming (Structured-Spec Design)

Follow the superpowers brainstorming *process* verbatim (explore context; one question at a
time; propose 2-3 approaches; present design sections with approval gates; spec self-review;
user review gate). This skill only changes the *output format* of the design doc.

**Announce at start:** "Using rdl-brainstorming to produce a structured spec."

Write the design doc to `{[project].docs_dir}/specs/YYYY-MM-DD-<topic>-design.md`. Commit only
if `[project].vcs = "git"`; otherwise write and report the skip.

## Design-doc structure

1. **Metadata block** — Dublin Core Terms + Schema.org (`TechArticle`). This is the chain-wide
   spine; Phase 5 scholarly-white-paper lifts it verbatim. See `references/notation.md`.
2. **Constraints** — RFC 2119 / BCP 14 keywords, normative ONLY in ALL-CAPS (RFC 8174). The
   manifest capability envelope enters here as `MUST` constraints.
3. **Acceptance criteria** — EARS, five patterns, each IDed `AC-n`. See `references/notation.md`.
4. **Architecture** — a single Structurizr `.dsl` model; C4 views are derived from it
   (correct-by-construction). **Structurizr DSL only** — no RDF/OWL architecture layer. Always
   write the `.dsl` source (text); render/validate only if structurizr is USABLE (granted ∧
   present — Plan-1 `schema.usable`), else log a skip naming the disabled feature
   (`architecture-rendering`). structurizr is an OPTIONAL dependency. Include this section only when the model has
   **≥2 elements** (decidable); a single-element design omits it (do not write "N/A").
5. **Decisions** — MADR records, IDed `ADR-n`; include only when a decision has **≥2 alternatives**.
6. **Glut register** — IDed `G-n`; record unresolved contradictions paraconsistently. Acceptance
   criteria in conflict are tagged `in-conflict`, NOT silently reconciled.

## The notation valve (Rice-correct)

Notation MUST NOT be scaled by auto-deciding task triviality — triviality is undecidable and
exceptional (Rice's theorem). Default treatment is **non-trivial**. The cheap layer (EARS +
RFC 2119) is **universal** — it reshapes sentences without adding sections, so it never bloats.
The expensive sections (Structurizr views, ADR, arc42 depth) are **content-gated on decidable
structural presence** (element count ≥2, alternative count ≥2), never on a triviality judgment.
Triviality MAY be asserted by the user as an explicit exception.

Validate the machine-checkable rules with `scripts/check_notation.py`.
```

- [ ] **Step 4: Write `BRAIN/references/notation.md`**

```markdown
# Notation Reference

## EARS (Easy Approach to Requirements Syntax) — five patterns
- **Ubiquitous:** `THE <system> SHALL <response>`
- **Event-driven:** `WHEN <trigger> THE <system> SHALL <response>`
- **State-driven:** `WHILE <state> THE <system> SHALL <response>`
- **Unwanted behavior:** `IF <condition> THEN THE <system> SHALL <response>`
- **Optional feature:** `WHERE <feature> THE <system> SHALL <response>`

## RFC 2119 / BCP 14 keywords (normative only in ALL-CAPS, per RFC 8174)
MUST / MUST NOT / REQUIRED / SHALL / SHALL NOT / SHOULD / SHOULD NOT / RECOMMENDED / MAY / OPTIONAL.

## Metadata spine (Dublin Core + Schema.org)
Embed a block with `dc:title`, `dc:creator`, `dc:subject`, `dc:description`, `dc:date`,
`dc:type`, `dc:language`, and a Schema.org `TechArticle`/`SoftwareSourceCode` `@type`.
Phase 5 (scholarly-white-paper) reuses this verbatim.

## MADR decision record shape
Context → Decision → Consequences → Alternatives rejected. One record per decision with ≥2
real alternatives.

## Glut register
`G-n: <the two conflicting claims> — status: open | reconciled(<how>)`. Paraconsistent: a live
contradiction is recorded, not forced to a premature resolution.
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd BRAIN && python3 -m pytest tests/test_brain_skill.py -q`
Expected: PASS (5 passed)

- [ ] **Step 6: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 3: `rdl-writing-plans` SKILL.md

**Files:**
- Create: `PLANW/SKILL.md`
- Test: `BRAIN/tests/test_planw_skill.py`

**Interfaces:**
- Consumes: `AC-n`/`ADR-n` IDs produced by `rdl-brainstorming` (Task 2); `plan_task_cites_ac` (Task 1).
- Produces: a plan skill enforcing RFC 2119 Global Constraints + AC→task→test traceability.

- [ ] **Step 1: Write the failing test**

```python
# BRAIN/tests/test_planw_skill.py
from pathlib import Path
PLANW = Path("/home/metavacua/.claude/skills/rdl-writing-plans")

def test_frontmatter_name():
    assert "name: rdl-writing-plans" in (PLANW / "SKILL.md").read_text()

def test_requires_traceability():
    t = (PLANW / "SKILL.md").read_text().lower()
    assert "ac-n" in t and "adr-n" in t
    assert "failing-test" in t or "failing test" in t
    assert "shall" in t  # test asserts the AC's SHALL clause

def test_rfc2119_global_constraints():
    assert "rfc 2119" in (PLANW / "SKILL.md").read_text().lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd BRAIN && python3 -m pytest tests/test_planw_skill.py -q`
Expected: FAIL — `FileNotFoundError`

- [ ] **Step 3: Write `PLANW/SKILL.md`**

```markdown
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd BRAIN && python3 -m pytest tests/test_planw_skill.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 4: Rewire RDL Phases 1/2 to the new subskills

**Files:**
- Modify: `RDL/SKILL.md` (Phase 1 heading ~line 60; Phase 2 heading ~line 70 — the `superpowers:brainstorming` / `superpowers:writing-plans` invocations)
- Test: `BRAIN/tests/test_rdl_rewired.py`

**Interfaces:**
- Consumes: `rdl-brainstorming`, `rdl-writing-plans` (Tasks 2/3).
- Produces: an RDL body whose Phase 1 invokes `rdl-brainstorming` and Phase 2 invokes `rdl-writing-plans`, while noting they inherit the superpowers process.

- [ ] **Step 1: Write the failing test**

```python
# BRAIN/tests/test_rdl_rewired.py
from pathlib import Path
SK = Path("/home/metavacua/.claude/skills/research-development-loop/SKILL.md").read_text()

def test_phase1_invokes_rdl_brainstorming():
    assert "rdl-brainstorming" in SK

def test_phase2_invokes_rdl_writing_plans():
    assert "rdl-writing-plans" in SK

def test_superpowers_process_still_credited():
    # inheritance is explicit, not a silent replacement
    low = SK.lower()
    assert "inherit" in low or "superpowers brainstorming process" in low
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd BRAIN && python3 -m pytest tests/test_rdl_rewired.py -q`
Expected: FAIL — `rdl-brainstorming` not present in RDL SKILL.md.

- [ ] **Step 3: Edit Phase 1.** Replace the Phase 1 invocation line (`Invoke superpowers:brainstorming.`) with:

```markdown
Invoke `rdl-brainstorming` (which inherits the superpowers brainstorming process and adds the
structured-spec notation layer). Do not enter Phase 2 until it reaches its terminal state.
```

- [ ] **Step 4: Edit Phase 2.** Replace the Phase 2 invocation line (`Invoke superpowers:writing-plans.`) with:

```markdown
Invoke `rdl-writing-plans` (inherits the superpowers writing-plans structure; adds RFC 2119
Global Constraints and AC→task→test traceability).
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd BRAIN && python3 -m pytest tests/test_rdl_rewired.py -q`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 5: Eval scenarios for the subskills

**Files:**
- Create: `BRAIN/evals/evals.json`
- Test: `BRAIN/tests/test_brain_evals.py`

**Interfaces:**
- Consumes: nothing (self-contained JSON).
- Produces: graded eval scenarios covering notation presence, the Rice-correct valve, Structurizr skip-logging, and traceability.

- [ ] **Step 1: Write the failing test**

```python
# BRAIN/tests/test_brain_evals.py
import json
from pathlib import Path
EVALS = Path("/home/metavacua/.claude/skills/rdl-brainstorming/evals/evals.json")

def test_parses():
    json.loads(EVALS.read_text())

def test_covers_valve_and_structurizr_and_traceability():
    names = [e["eval_name"] for e in json.loads(EVALS.read_text())["evals"]]
    for expected in ["valve-no-auto-triviality", "structurizr-skip-when-ungranted", "ac-task-test-traceability"]:
        assert expected in names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd BRAIN && python3 -m pytest tests/test_brain_evals.py -q`
Expected: FAIL — `FileNotFoundError`

- [ ] **Step 3: Write `BRAIN/evals/evals.json`**

```json
{
  "skill_name": "rdl-brainstorming",
  "evals": [
    {
      "id": 1,
      "eval_name": "valve-no-auto-triviality",
      "prompt": "Design a one-line config change and, separately, a three-component service. Produce specs.",
      "expected_output": "Both specs use EARS acceptance criteria and RFC 2119 constraints (universal cheap layer). The one-line change OMITS the Structurizr architecture section (only 1 element) and the ADR section (no >=2-alternative decision) — by content-gating, not by declaring the task 'trivial'. The three-component service INCLUDES a Structurizr .dsl model with a derived C4 view. The skill never claims to have decided triviality algorithmically.",
      "assertions": [
        { "name": "cheap-layer-universal", "description": "Both specs contain EARS ACs and ALL-CAPS RFC 2119 keywords" },
        { "name": "arch-content-gated", "description": "Architecture section present iff >=2 elements; absent section is omitted, not written as 'N/A'" },
        { "name": "no-triviality-judgment", "description": "The skill does not auto-decide task triviality to scale notation" }
      ],
      "files": []
    },
    {
      "id": 2,
      "eval_name": "structurizr-skip-when-ungranted",
      "prompt": "Produce a multi-component design in an environment where structurizr is not usable (either ungranted, or granted but not installed).",
      "expected_output": "The architecture.dsl source is still written (text needs no capability). Because structurizr is an OPTIONAL dependency, rendering/validation is skipped with a logged reason that NAMES the disabled feature (architecture-rendering) and the failing axis (need-grant vs need-install) — never a silent no-op and never a claim that the diagram was rendered.",
      "assertions": [
        { "name": "dsl-source-written", "description": "architecture.dsl is authored regardless of usability" },
        { "name": "render-skip-names-feature", "description": "Render/validate emits a logged skip naming the disabled feature and the failing axis when structurizr is not usable" }
      ],
      "files": []
    },
    {
      "id": 3,
      "eval_name": "ac-task-test-traceability",
      "prompt": "Given a design doc with AC-1..AC-3, hand off to rdl-writing-plans and inspect the plan.",
      "expected_output": "Every plan task cites a live AC-n and the ADR-n that justifies it; each failing-test step asserts that AC's SHALL clause; no task cites a dangling AC not present in the design.",
      "assertions": [
        { "name": "tasks-cite-live-acs", "description": "Each task references an AC-n that exists in the design; no dangling references" },
        { "name": "test-asserts-shall", "description": "The failing-test step asserts the cited AC's SHALL clause" }
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd BRAIN && python3 -m pytest tests/test_brain_evals.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Run the full Plan-2 suite**

Run: `cd BRAIN && python3 -m pytest tests/ -q`
Expected: PASS (all Plan-2 tests green)

- [ ] **Step 6: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none — Plan 2 (D-B) complete"
```

---

## Self-Review

**Spec coverage:** C-NOTRIVIA → T1 (`test_content_gating_thresholds`) + T2 (`test_valve_is_rice_correct`) + T5 eval #1; C-GLUT → T2 (`test_declares_all_notation_sections` includes glut register) + notation.md; C-COBC / Structurizr-only → T1 (`test_structurizr_action_gated`) + T2 (`test_structurizr_only_no_rdf_architecture`) + T5 eval #2; C-SPINE (Dublin Core + Schema.org) → T2 metadata section; AC-8 → T2; AC-9/AC-10 (content-gating) → T1 thresholds + T5 eval #1; AC-11 (traceability) → T1 (`plan_task_cites_ac`) + T3 + T5 eval #3; AC-12 (structurizr skip) → T1 + T5 eval #2; C-UNTOUCHED → all new files under `rdl-*`, RDL rewired in T4 without touching the plugin.

**Placeholder scan:** no TBD/TODO; every code step is complete; every prose SKILL edit ships with a grep/parse test.

**Type consistency:** `classify_ears`/`is_ears`/`normative_keywords`/`arch_section_required`/`adr_required`/`structurizr_action`/`plan_task_cites_ac` signatures identical across T1 tests and their T3/T5 consumers. `AC-n`/`ADR-n`/`G-n` ID conventions identical across T2 (design), T3 (plan), and T5 (evals). Manifest keys (`[project].docs_dir`, `[project].vcs`, `[capabilities].subprocess`) match Plan 1's schema exactly.

Gap check: the prose valve rule (Rice) is not directly executable, so it is covered by (a) the decidable-threshold unit tests in T1 and (b) the `valve-no-auto-triviality` eval in T5 — the executable proxy. Acceptable per the design.
