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
