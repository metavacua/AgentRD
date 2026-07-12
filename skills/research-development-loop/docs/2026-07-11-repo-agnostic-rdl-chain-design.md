<!--
Dublin Core / Schema.org metadata (chain-wide spine; Phase 5 scholarly-white-paper lifts this verbatim)
dc:title        Repository- and Toolchain-Agnostic RDL Chain with Industry-Standard Spec Notation
dc:creator      Claude Opus 4.8 (research-development-loop / brainstorming) 2026-07-11
dc:subject      research-development-loop; capability manifest; least-privilege; EARS; RFC 2119; MADR; arc42; C4; Structurizr; Dublin Core; Schema.org
dc:description  Design for making the local RDL chain repo/toolchain-agnostic via a mandatory least-privilege capability manifest, plus two RDL-owned notation subskills.
dc:date         2026-07-11
dc:type         SoftwareSourceCode / TechArticle (design spec)
dc:language     en
schema:@type    TechArticle
-->

# Repository- and Toolchain-Agnostic RDL Chain — Design Spec

**Goal:** Make the local `research-development-loop` chain (`research-development-loop`, `research-phase`) repository- and toolchain-agnostic by extracting all project-specific assumptions into a mandatory least-privilege capability manifest, and add two RDL-owned notation subskills (`rdl-brainstorming`, `rdl-writing-plans`) that produce industry-standard structured specs.

**Default target:** a constrained sandbox (`wasm32v1-none`-class) — zero ambient authority. No network, filesystem, clock, entropy, threads, GPU, subprocess, or "system RAM is free" is assumed until explicitly granted.

**Scope — two coupled deliverables (one design → two implementation plans):**
- **D-A — Agnostic chain:** the `rdloop.toml` manifest + de-hardcoding `research-development-loop` and `research-phase` and their `references/`.
- **D-B — Notation subskills:** new local `rdl-brainstorming` + `rdl-writing-plans`; the superpowers plugin is left untouched.

They couple through the manifest (D-B reads `[project].docs_dir`/`vcs`; D-A Phases 1/2 invoke D-B).

---

## Constraints (RFC 2119 / BCP 14 — normative when ALL-CAPS)

- **C-MANIFEST:** The chain MUST require an `rdloop.toml` manifest. When absent, it MUST scaffold a minimal *non-trivial* manifest (all required sections present, populated with least-privilege values), write it, and pause for user review. It MUST NOT run on implicit in-memory defaults.
- **C-LEASTPRIV:** The base manifest MUST encode explicit zero-ambient-authority. Every capability (filesystem, network, subprocess, clock, random, threads, gpu) MUST default to denied. `memory_budget_mb` MUST be a finite small value, never `0`/unlimited. Default `security.default_posture` MUST be `deny`.
- **C-AGNOSTIC:** The `SKILL.md` bodies of `research-development-loop` and `research-phase` MUST NOT contain hardcoded project identifiers (metavacua/*, chrishayuk/*, larql, pi-harness, bin/coding-agent, 6.3 GB/no-swap). Each MUST be replaced by a manifest lookup. Metavacua SHOULD survive only as an example manifest.
- **C-NOSILENT:** Any step that shells out and finds no matching capability grant MUST NOT silently no-op. It MUST either (non-critical) log a skip and continue, or (critical) raise a user prompt and halt. A shell-out step MUST NEVER produce a false-clean.
- **C-CRITICALITY:** Criticality MUST be declared per step, not decided algorithmically (Rice: triviality is undecidable and exceptional).
- **C-NOTRIVIA:** The notation valve MUST NOT auto-decide task triviality. Default treatment is non-trivial. Cheap notation (EARS, RFC 2119) MUST be universal. Expensive sections (Structurizr views, ADR, arc42) MUST be gated on decidable structural presence (element/alternative counts), not on a triviality judgment. Triviality MAY be asserted by the user as an exception.
- **C-GLUT:** The design-doc format MUST provide a first-class glut register for recording unresolved contradictions paraconsistently. Consistency MUST NOT be forced by silent reconciliation.
- **C-COBC:** Architecture diagrams MUST be correct-by-construction views derived from a single machine-readable model (Structurizr DSL). Hand-drawn diagrams that can drift from the model MUST NOT be the source of truth.
- **C-SPINE:** Document metadata MUST use Dublin Core Terms + Schema.org, shared verbatim with the Phase 5 `scholarly-white-paper` stack.
- **C-UNTOUCHED:** The superpowers plugin skills MUST NOT be edited. New behavior lives in RDL-owned local skills.
- **C-USABLE:** Usable capability MUST be computed as `U = G ∩ E` where `G` = granted (manifest permission) and `E` = extant (environment-resolved presence). Permission and presence are each necessary and jointly sufficient. The chain MUST check the global precondition — `U ≠ ∅` and every REQUIRED step's needs ⊆ `U` — BEFORE doing work, and MUST halt with a prompt if the configuration is incapable. It MUST NOT expend research/dev effort on an incapable configuration.
- **C-DEPRESOLVE:** The dependency axis MUST be DELEGATED to a recognized native manifest standard (`[dependencies].standard` ∈ {cargo, pep621, maven, …}; default `cargo`) — REFERENCED, never re-declared in `rdloop.toml`. Off-list is an explicit flagged opt-in (`standard = "custom"`), never the default. Declared deps + toolchain MUST be RESOLVED (presence-checked) by parsing the native manifest. A missing REQUIRED dependency MUST halt with a prompt (*install x*), never skipped or inferred as "not needed." A missing OPTIONAL dependency MUST log a skip NAMING the disabled feature. Unusability MUST be diagnosed to the failing axis (need-grant / need-install / need-both), never a bare skip.

---

## Acceptance Criteria (EARS)

- **AC-1 (event):** WHEN the chain starts and no `rdloop.toml` is found on an upward walk from cwd, the chain SHALL scaffold the minimal non-trivial base manifest, write it, and pause for user review.
- **AC-2 (state):** WHILE `[project].vcs = "none"`, the chain SHALL write spec/plan artifacts without invoking git, and SHALL report that no commit was made.
- **AC-3 (event):** WHEN `[project].vcs = "git"` and a spec/plan is finalized, the chain SHALL commit it.
- **AC-4 (unwanted):** IF a step shells out to a capability absent from the manifest grants AND the step is non-critical, THEN the chain SHALL log a skip naming the missing grant and continue.
- **AC-5 (unwanted):** IF a step shells out to a capability absent from the manifest grants AND the step is critical, THEN the chain SHALL raise a user prompt naming the missing capability and the exact grant that satisfies it, and SHALL halt until resolved.
- **AC-6 (unwanted):** IF a step shells out to an ungranted capability, THEN the chain SHALL NOT proceed as though the step succeeded (no false-clean).
- **AC-7 (ubiquitous):** The `research-phase` steps 0.3/0.4/0.5/0.6 SHALL each consult the manifest before shelling out, and SHALL be governed by the same skip/prompt rule as the rest of the chain.
- **AC-8 (ubiquitous):** `rdl-brainstorming` output SHALL include a Dublin Core + Schema.org metadata block, RFC 2119 constraints, EARS acceptance criteria with `AC-n` IDs, and a glut register.
- **AC-9 (event):** WHEN a `rdl-brainstorming` design contains ≥2 architecture elements, it SHALL include a Structurizr `.dsl` model and a C4 view derived from it; otherwise it SHALL omit the architecture-view section (not write "N/A").
- **AC-10 (event):** WHEN a `rdl-brainstorming` design contains a decision with ≥2 alternatives, it SHALL include a MADR record for it; otherwise it SHALL omit the decisions section.
- **AC-11 (ubiquitous):** Every `rdl-writing-plans` task SHALL cite the `AC-n` it satisfies and the `ADR-n` that justifies it, and its failing-test step SHALL assert that AC's `SHALL` clause.
- **AC-12 (state):** WHILE the Structurizr toolchain is unresolved (declared optional, absent from the environment), `rdl-brainstorming` SHALL still write the `.dsl` source and SHALL log a skip that NAMES the disabled feature ("architecture-rendering").
- **AC-13 (event):** WHEN the chain starts, it SHALL resolve `E` (present capabilities) against `G` (granted capabilities), compute `U = G ∩ E`, and SHALL halt with a prompt if `U = ∅` or any required step's needs are not ⊆ `U`.
- **AC-14 (unwanted):** IF a REQUIRED dependency declared in the referenced native manifest (`[dependencies].manifest`) is not present in the environment, THEN the chain SHALL halt with a prompt naming the tool and the install action, and SHALL NOT skip it or proceed.
- **AC-16 (unwanted):** IF `[dependencies].standard` is not a recognized standard AND is not the explicit `"custom"` opt-in, THEN the chain SHALL halt (unrecognized manifest standard); WHERE it is `"custom"`, the chain SHALL proceed but SHALL flag the configuration as off-standard.
- **AC-15 (unwanted):** IF a capability is unusable, THEN the chain SHALL diagnose which axis failed (need-grant vs need-install vs need-both) and SHALL emit the axis-specific remedy, never a bare skip.

---

## Architecture

### §1 — `rdloop.toml`: least-privilege capability manifest

Format TOML (2026 default for human-edited manifests). Discovery: walk up from cwd. Absent ⇒ scaffold the base below, write, pause (AC-1). Model: WASI Preview 2 zero-ambient-authority + iframe-sandbox deny-all allowlist.

```toml
[project]
name = "unnamed-project"; target = "wasm32v1-none"; docs_dir = "docs/superpowers"; vcs = "none"

[capabilities]              # everything DENIED until granted (allowlist)
filesystem = []            # granted paths (preopens); [] = none
network    = []            # granted hosts;            [] = none
subprocess = []            # granted commands;         [] = none
clock = false; random = false; threads = false; gpu = false

[dependencies]             # REQUIREMENT axis — REFERENCE a recognized native manifest, never re-declare
standard  = "cargo"        # recognized standard (cargo|pep621|maven|…); "custom" = flagged off-list opt-in
manifest  = "Cargo.toml"   # deps resolved by PARSING this native file (not re-declared here)
toolchain = "rust-toolchain.toml"   # recognized toolchain-pin standard (optional)
# required dep/toolchain missing in the environment → HALT + prompt (install x);
# optional missing → skip + name disabled feature. Presence resolved, never declared here.

[resources]
memory_budget_mb = 64      # finite; never 0/unlimited
serialize_tasks  = true    # no parallel resource-heavy work (OOM safety)

[issues]
tracker = "none"; write_repos = []; read_repos = []

[delegation]
subagent = "inline"

[security]
default_posture = "deny"; write_allowed = []

[x]                        # forward-compat extension hatch (Cargo workspace.metadata style)
```

Metavacua becomes `references/example-manifest.metavacua.toml`, granting up from this floor (github tracker, metavacua write_repos, chrishayuk read-only, 6300 MB budget + serialize, larql-probe/pi-harness subprocess grants).

### §2 — Extraction map (13 rows)

Each hardcoded specific becomes a manifest lookup; the body keeps only the generic mechanism.

| # | Source | Today | → Manifest |
|---|---|---|---|
| 1 | research-phase 0.4/0.3 | `gh … --repo metavacua/*` | `[issues].tracker`+`read_repos` (tracker=none ⇒ skip 0.4) |
| 2 | research-phase 0.6 | larql vindex / subagent graph query | `[x].graph_context` (absent ⇒ no-op) |
| 3 | RDL Phase 3 + references/delegation.md | pi-harness / ollama | `[delegation].*` + `[capabilities].subprocess` |
| 4 | RDL Phase 3 (104) | `bin/coding-agent` demo runner | `[delegation].demo_runner` |
| 5 | RDL Phase 5 + issue-governance.md | metavacua↔larql routing; never chrishayuk | `[issues].write_repos`/`read_repos` (read-only = in read, not write; special-case deleted) |
| 6 | RDL Resource Safety | 6.3 GB/no-swap; larql-server; 2 GB preflight | `[resources].*` + subprocess grant |
| 7 | RDL Security | metavacua-only writes; ~/larql read-only | `[security]` + `[issues].write_repos` + `[capabilities].filesystem` (ungranted path = denied; rule deleted) |
| 8 | RDL state label (22) | "larql subagent + TDD" | generic "coding subagent + TDD" |
| 9 | references/dependency-exploration.md, hooks-architecture.md | babel-harness fixtures; pi-harness dispatch | genericized; specifics → labeled examples |
| 10 | research-phase 0.3 (43–45) | `git branch/status/log` unconditional | `[project].vcs` gates all git cmds; none ⇒ read files directly |
| 11 | research-phase 0.5 (81–101) | assumed uv/pip/pytest/npm/go/cargo | run only toolchains in `[capabilities].subprocess`; else skip (logged) |
| 12 | research-phase 0.5/0.6 | `scripts/*.py` + python3 | `[x].graph_context` + subprocess grant |
| 13 | gh / git tool availability | assumed ambient | `[capabilities].subprocess` must list them; ungranted ⇒ skip/prompt |

Two structural wins: the chrishayuk "GET-only" and `~/larql` "read-only" special-case rules are **deleted, not ported** — they are the default state under deny-by-default.

### §3 — Notation subskills

`rdl-brainstorming` design-doc structure: Dublin Core+Schema.org metadata · RFC 2119 constraints · EARS acceptance criteria (`AC-n`) · Architecture backed by a single Structurizr `.dsl` model with derived C4 views (present iff ≥2 elements) · MADR decisions (present iff ≥2 alternatives) · **glut register** (`G-n`, paraconsistent). `rdl-writing-plans` = superpowers writing-plans + traceability: RFC 2119 Global Constraints; each task cites `AC-n`+`ADR-n`; failing-test asserts the AC's `SHALL`.

**Valve (Rice-correct):** no triviality tiers, no auto-detection. Default non-trivial. Cheap notation (EARS/RFC 2119) universal (reshapes sentences, adds no sections). Expensive sections gated on decidable structural presence. Triviality is a user-asserted exception only.

**Machine-readable model:** Structurizr DSL only (C4 reference impl; correct-by-construction; git-diffable). No RDF/OWL architecture projection. Dublin Core+Schema.org *document* metadata retained (Phase-5 spine).

### §4 — Output, error-handling, testing

- Output: `{docs_dir}/specs|plans/`. Commit only if `vcs="git"` (AC-2/AC-3); non-git ⇒ write + report skip.
- **Capability precondition first (AC-13):** resolve `E`, compute `U = G ∩ E`; if `U = ∅` or a required step's needs ⊄ `U`, halt with a prompt before any work.
- **Usability + diagnosis (AC-15):** a step needing `x` runs iff `x ∈ U`; otherwise diagnose the axis — `x ∈ E\G` (need-grant), `x ∈ G\E` (need-install), `x ∉ G∪E` (need-both) — and emit the axis-specific remedy.
- **Required vs optional (AC-4/5/6/14):** required-missing (either axis) → user prompt + halt; optional-missing → logged skip that NAMES the disabled feature. Never a bare skip, never a false-clean.
- Default classification: **required** = the loop's own test runner (`python`/`pytest`), the ability to write the artifact, a subagent when no inline fallback exists, a well-formed manifest; **optional** = issue tracker (0.4/Phase 5), graph-context (0.6), git context (0.3), Structurizr render (declared optional → absence disables "architecture-rendering", `.dsl` still authored). *(Correction of a prior error: a bare sandbox lacking `python`/`pytest` does NOT "skip everything" — those are required, so the loop declares itself incapable and halts.)*
- Testing: eval scenarios in the existing `evals/evals.json` + skill-creator harness; TDD per machine-checkable artifact (TOML parse+schema, scaffold completeness, EARS pattern match, RFC 2119 all-caps, `.dsl` validates-when-granted / logs-skip-when-not, task↔AC linkage). Bare-sandbox fixture (no git/gh/toolchains) asserts every shell-out logs a skip and nothing false-cleans.

---

## Decisions (MADR)

- **ADR-1 — Manifest is mandatory, scaffold-on-absence.** Context: optional-with-defaults hides assumptions and enables silent false-cleans. Decision: require it; absent ⇒ scaffold minimal non-trivial + pause. Consequences: one bootstrap step; no implicit-default drift. Alternatives rejected: optional manifest; frontmatter defaults.
- **ADR-2 — Zero-ambient-authority default (`wasm32v1-none`-class).** Context: the old skill assumed a specific 6.3 GB host with ambient tools. Decision: deny-by-default capability model (WASI/iframe-sandbox). Consequences: constrained targets are first-class; grants are explicit; more steps skip/prompt by default. Alternatives rejected: conservative-but-open defaults; "ask" posture.
- **ADR-3 — New RDL-owned subskills, superpowers untouched.** Alternatives rejected: shadow-override same names (leaks to all callers); thin wrapper (indirection).
- **ADR-4 — Structurizr DSL only for the architecture model.** Context: diagrams must be machine-readable and correct-by-construction. Decision: C4-as-code, no RDF/OWL layer. Consequences: diffable, AI-friendly, no SPARQL surface. Alternatives rejected: RDF/OWL-first (authoring cost); Mermaid-as-source (drift).
- **ADR-5 — No triviality tiers; content-gated notation.** Context: Rice — triviality is undecidable and exceptional. Decision: default non-trivial; gate on decidable structural presence. Consequences: sound valve; Fowler's verbosity concern met without an unsound judgment. Alternatives rejected: T0/T1/T2 auto-proposed tiers.
- **ADR-6 — Criticality-gated skip/prompt.** Decision: declared criticality routes ungranted steps to skip (non-critical) or user prompt (critical). Alternatives rejected: uniform skip (limps forward on critical gaps); uniform prompt (nags on optional gaps in the constrained default).
- **ADR-7 — Capability = granted ∧ present; grant table + referenced native dependency manifest.** Context: permission (WASI grant) and presence (dependency) are orthogonal necessary conditions; usable = their intersection `U = G ∩ E`; `U = ∅` ⇒ incapable ⇒ halt. Decision: keep the grant allowlist (`[capabilities]`) bespoke (it is least-privilege policy), but DELEGATE the dependency axis to a recognized native manifest via `[dependencies]` (default `cargo` → `Cargo.toml` + `rust-toolchain.toml`); resolve deps by parsing it; off-list is a flagged `custom` opt-in. Consequences: no reinvented dependency table (E3); fail-fast on missing required deps (K19); Cargo default coheres with the wasm-sandbox target (C17). Alternatives rejected: **bespoke `[toolchains]` table** (E3 — reinvents Cargo/pyproject/POM; "bespoke where a standard exists is always wrong"); unified per-tool entry; treating a missing required tool as a capability-skip (the original conflation error).

---

## Glut register

- *(none open)* — the one apparent tension (user's earlier RDF/SPARQL emphasis vs. the "Structurizr DSL only" decision) was **reconciled, not left as a glut:** Structurizr's model is itself a machine-readable graph; Dublin Core/Schema.org document metadata is retained; only the separate RDF architecture projection was dropped. Recorded here per C-GLUT so the reconciliation is auditable.

---

## Negative inventory (N — confirmed absences / silent-failure modes)

- **N1:** Notation does not guarantee agent compliance (Fowler: agents ignore specs regardless of rigor). This design improves *requirement testability + traceability*, NOT adherence.
- **N2:** EARS cannot express architecture/rationale/NFRs — that gap is why the ADR + Structurizr sections exist.
- **N3 (dissolved):** plugin-cache persistence risk — dissolved by targeting local RDL-owned skills (C-UNTOUCHED).
- **N4:** vendor "3–10× first-pass" figures are unverified here; not relied upon.
- **N5–N7:** git/toolchain/gh assumed-ambient ⇒ false-clean in a bare cwd. Mitigated by C-NOSILENT + AC-4/5/6; the bare-sandbox test fixture exercises exactly this.
- **N8 (new):** criticality is *declared*, so a misclassification (marking a critical step optional) would skip-and-limp silently. Mitigation: default table above errs toward `critical` for anything touching the artifact output or task feasibility; classifications are reviewable in the plan.

---

## Research residual (canonical knowledge state)

K1–K23, C1–C17, E1–E3, N1–N9, A1–A2 as accumulated across Phase 0 + micro-cycles (SDD/EARS/RFC2119/MADR/arc42; SBOM/Cargo-workspace/TOML manifest; WASI/iframe/wasm-target least-privilege; Structurizr machine-readable model; Rice triviality; scholarly-white-paper spine; capability = granted ∧ present with `U = G ∩ E` precondition; dependency axis delegated to a recognized native manifest, Cargo default cohering with the wasm-sandbox target; E3 = no bespoke toolchain table). Full entries in the conversation thread; this spec is their consolidation.
