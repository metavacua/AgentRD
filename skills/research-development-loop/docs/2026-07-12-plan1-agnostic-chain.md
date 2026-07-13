> **Historical record (superseded).** This dated plan documents work completed *before* the `superpowers` decoupling of 2026-07-12. Its `superpowers` / `docs/superpowers` references are preserved as a record, not current guidance. Current design: `docs/plans/2026-07-12-decouple-rdl-from-superpowers.md`.

# Plan 1 (D-A) — Repository/Toolchain-Agnostic RDL Chain — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract every project-specific assumption out of the `research-development-loop` and `research-phase` skill bodies into a mandatory least-privilege `rdloop.toml` manifest, so the chain runs correctly in any repo/toolchain/sandbox.

**Architecture:** A Python module (`rdloop/schema.py`, stdlib `tomllib` only) owns manifest scaffold/load/validate/gate and is fully unit-tested. The two `SKILL.md` bodies and `references/*.md` are edited to replace hardcoded identifiers with manifest lookups; a grep-based test asserts the identifiers are gone. Metavacua survives only as `references/example-manifest.metavacua.toml`.

**Tech Stack:** Python 3.11 (`tomllib` stdlib), pytest 7.2, Markdown SKILL files, TOML manifests.

## Global Constraints

- **C-MANIFEST:** manifest is mandatory; absent ⇒ scaffold minimal non-trivial base + pause. No implicit in-memory defaults.
- **C-LEASTPRIV:** all capabilities default denied; `memory_budget_mb` finite >0 (never 0/unlimited); `security.default_posture = "deny"`.
- **C-AGNOSTIC:** no hardcoded `metavacua`/`chrishayuk`/`babel-harness`/`larql`/`pi-harness`/`bin/coding-agent`/`ollama`/`6.3 GB` in the SKILL bodies; each becomes a manifest lookup. Metavacua only as an example file.
- **C-NOSILENT:** ungranted shell-out step never silently no-ops.
- **C-CRITICALITY:** non-critical ungranted ⇒ logged skip; critical ungranted ⇒ user prompt + halt. Criticality declared per step, never auto-judged.
- **C-USABLE:** usable `U = G ∩ E` (granted ∧ present). Check `U ≠ ∅` and required-steps ⊆ `U` before work; else halt. Never work an incapable configuration.
- **C-DEPRESOLVE:** the dependency axis is DELEGATED to a recognized native manifest (`[dependencies].standard`, default `cargo` → `Cargo.toml`; off-list = flagged `custom`). Deps resolved by PARSING it; required-missing ⇒ halt+prompt (*install x*), never a skip/"not needed"; optional-missing ⇒ logged skip naming the disabled feature; diagnose the failing axis (need-grant/need-install/need-both). No bespoke toolchain table (E3).
- **vcs=none here:** `/home/metavacua` is not a git repo, so every "Commit" step is a logged no-op (skip reported), per C-NOSILENT. Run `git add`/`commit` only if the skill dir is later placed under git.
- **Base path:** all paths are under `~/.claude/skills/research-development-loop/` unless stated. Written as `RDL/` below = `/home/metavacua/.claude/skills/research-development-loop/`.

---

### Task 1: Manifest core — scaffold, find, load, validate, gate

**Files:**
- Create: `RDL/rdloop/schema.py`
- Test: `RDL/tests/test_manifest.py`

**Interfaces:**
- Produces: `scaffold() -> str`; `find_manifest(start) -> Path|None`; `load(path) -> dict`; `validate(m: dict) -> None` (raises `ManifestError`; rejects an unrecognized `[dependencies].standard` unless the explicit `custom` opt-in); `RECOGNIZED_STANDARDS`; `parse_native_deps(standard, manifest_path) -> set[str]` (cargo via `tomllib`); `granted(m, kind, name) -> bool`; `gate(m, kind, name, critical) -> str` (`"run"|"skip"|"prompt"`); `usable(m, present_set, name) -> bool`; `diagnose(m, present_set, name) -> str` (`"ok"|"need-grant"|"need-install"|"need-both"`); `capability_precondition(m, present_set, required_names) -> tuple[bool, str]`; module constants `REQUIRED_SECTIONS`, `CAP_LIST`, `CAP_BOOL`.

- [ ] **Step 1: Write the failing tests**

```python
# RDL/tests/test_manifest.py
import tomllib
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema

def test_scaffold_parses_as_toml():
    tomllib.loads(schema.scaffold())  # must not raise

def test_scaffold_has_all_required_sections():
    m = tomllib.loads(schema.scaffold())
    for s in schema.REQUIRED_SECTIONS:
        assert s in m, f"scaffold missing [{s}]"

def test_scaffold_is_least_privilege():
    m = tomllib.loads(schema.scaffold())
    caps = m["capabilities"]
    assert caps["filesystem"] == [] and caps["network"] == [] and caps["subprocess"] == []
    assert caps["clock"] is False and caps["gpu"] is False
    assert m["resources"]["memory_budget_mb"] > 0
    assert m["security"]["default_posture"] == "deny"
    assert m["project"]["vcs"] == "none"

def test_validate_rejects_missing_section():
    m = tomllib.loads(schema.scaffold())
    del m["capabilities"]
    with pytest.raises(schema.ManifestError):
        schema.validate(m)

def test_validate_rejects_unlimited_memory():
    m = tomllib.loads(schema.scaffold())
    m["resources"]["memory_budget_mb"] = 0
    with pytest.raises(schema.ManifestError):
        schema.validate(m)

def test_validate_accepts_base():
    schema.validate(tomllib.loads(schema.scaffold()))  # must not raise

def test_gate_run_skip_prompt():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["gh"]
    assert schema.gate(m, "subprocess", "gh", critical=False) == "run"
    assert schema.gate(m, "subprocess", "git", critical=False) == "skip"
    assert schema.gate(m, "subprocess", "git", critical=True) == "prompt"

def test_find_manifest_walks_up(tmp_path):
    (tmp_path / "rdloop.toml").write_text(schema.scaffold())
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert schema.find_manifest(deep) == tmp_path / "rdloop.toml"

def test_find_manifest_absent(tmp_path):
    assert schema.find_manifest(tmp_path) is None

def test_scaffold_has_dependencies_section():
    m = tomllib.loads(schema.scaffold())
    assert "dependencies" in m
    assert m["dependencies"]["standard"] == "cargo"          # restrictive default

def test_validate_rejects_unrecognized_standard():
    m = tomllib.loads(schema.scaffold())
    m["dependencies"]["standard"] = "myhomegrownthing"
    with pytest.raises(schema.ManifestError):
        schema.validate(m)

def test_validate_allows_explicit_custom_optin():
    m = tomllib.loads(schema.scaffold())
    m["dependencies"]["standard"] = "custom"                 # off-list opt-in is allowed (flagged elsewhere)
    schema.validate(m)

def test_parse_native_deps_cargo(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname="x"\n[dependencies]\nserde="1"\ntokio={version="1"}\n')
    assert schema.parse_native_deps("cargo", tmp_path / "Cargo.toml") == {"serde", "tokio"}

def test_diagnose_three_axes():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["git", "python"]      # granted
    present = {"python", "gh"}                                 # python + gh present; gh NOT granted
    assert schema.diagnose(m, present, "python") == "ok"          # granted & present
    assert schema.diagnose(m, present, "git") == "need-install"   # granted, not present
    assert schema.diagnose(m, present, "gh") == "need-grant"      # present, NOT granted
    m2 = tomllib.loads(schema.scaffold())
    assert schema.diagnose(m2, set(), "gh") == "need-both"        # neither granted nor present

def test_usable_is_intersection():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["python"]
    assert schema.usable(m, {"python"}, "python") is True
    assert schema.usable(m, set(), "python") is False        # granted, not present
    assert schema.usable(m, {"git"}, "git") is False         # present, not granted

def test_precondition_incapable_when_required_missing():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["python"]
    ok, reason = schema.capability_precondition(m, present_set=set(), required_names=["python"])
    assert ok is False and "python" in reason               # required dep absent -> incapable

def test_precondition_capable_when_required_present():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["python"]
    ok, _ = schema.capability_precondition(m, present_set={"python"}, required_names=["python"])
    assert ok is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd RDL && python3 -m pytest tests/test_manifest.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'rdloop'`

- [ ] **Step 3: Create the package init**

```python
# RDL/rdloop/__init__.py
```
(empty file)

- [ ] **Step 4: Write the schema module**

```python
# RDL/rdloop/schema.py — rdloop.toml manifest: scaffold, find, load, validate, gate.
import tomllib
from pathlib import Path

REQUIRED_SECTIONS = ("project", "capabilities", "dependencies", "resources", "issues", "delegation", "security")
CAP_LIST = ("filesystem", "network", "subprocess")
CAP_BOOL = ("clock", "random", "threads", "gpu")
RECOGNIZED_STANDARDS = ("cargo", "pep621", "maven")  # extend as standards are added; "custom" = off-list opt-in

BASE_MANIFEST = '''# rdloop.toml — Research-Development-Loop manifest (minimal non-trivial base).
# Model: zero ambient authority (WASI Preview 2) + deny-all allowlist (iframe sandbox).
# Every capability is DENIED unless explicitly granted. Absent = denied.

[project]
name = "unnamed-project"
target = "wasm32v1-none"
docs_dir = "docs/superpowers"
vcs = "none"

[capabilities]
filesystem = []
network = []
subprocess = []
clock = false
random = false
threads = false
gpu = false

[dependencies]
standard = "cargo"
manifest = "Cargo.toml"
toolchain = "rust-toolchain.toml"

[resources]
memory_budget_mb = 64
serialize_tasks = true

[issues]
tracker = "none"
write_repos = []
read_repos = []

[delegation]
subagent = "inline"

[security]
default_posture = "deny"
write_allowed = []

[x]
'''

class ManifestError(ValueError):
    pass

def scaffold() -> str:
    """Minimal non-trivial base manifest: all required sections, least-privilege values."""
    return BASE_MANIFEST

def find_manifest(start) -> Path | None:
    """Walk up from `start` for rdloop.toml. Return its Path or None."""
    start = Path(start).resolve()
    for d in (start, *start.parents):
        cand = d / "rdloop.toml"
        if cand.is_file():
            return cand
    return None

def load(path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)

def validate(m: dict) -> None:
    """Raise ManifestError on any structural or least-privilege violation."""
    for s in REQUIRED_SECTIONS:
        if s not in m:
            raise ManifestError(f"missing required section [{s}]")
    caps = m["capabilities"]
    for c in CAP_LIST:
        if not isinstance(caps.get(c), list):
            raise ManifestError(f"capabilities.{c} must be a list")
    for c in CAP_BOOL:
        if not isinstance(caps.get(c), bool):
            raise ManifestError(f"capabilities.{c} must be a bool")
    mb = m["resources"].get("memory_budget_mb")
    if not isinstance(mb, int) or isinstance(mb, bool) or mb <= 0:
        raise ManifestError("resources.memory_budget_mb must be a positive int (never 0/unlimited)")
    if m["security"].get("default_posture") not in ("deny", "allow"):
        raise ManifestError("security.default_posture must be 'deny' or 'allow'")
    if m["project"].get("vcs") not in ("git", "none"):
        raise ManifestError("project.vcs must be 'git' or 'none'")
    std = m["dependencies"].get("standard")
    if std not in RECOGNIZED_STANDARDS and std != "custom":
        raise ManifestError(
            f"dependencies.standard '{std}' is not recognized; use one of "
            f"{RECOGNIZED_STANDARDS} or the explicit 'custom' off-list opt-in")

def parse_native_deps(standard: str, manifest_path) -> set:
    """Return the dependency names declared in the referenced native manifest.
    cargo/pep621 are TOML (parsed via tomllib). Extend per standard as needed."""
    if standard in ("cargo", "pep621"):
        with open(manifest_path, "rb") as f:
            data = tomllib.load(f)
        if standard == "cargo":
            return set(data.get("dependencies", {}).keys())
        return set(data.get("project", {}).get("dependencies", []))  # PEP 621 list
    raise ManifestError(f"parse_native_deps: standard '{standard}' not yet supported")

def granted(m: dict, kind: str, name: str) -> bool:
    """True iff capability `name` of `kind` (filesystem/network/subprocess) is granted (G)."""
    return name in m["capabilities"].get(kind, [])

def gate(m: dict, kind: str, name: str, critical: bool) -> str:
    """Route an ungranted shell-out. Returns 'run' | 'skip' | 'prompt' — never silent."""
    if granted(m, kind, name):
        return "run"
    return "prompt" if critical else "skip"

def usable(m: dict, present_set, name: str) -> bool:
    """U = G ∩ E: usable iff granted (as a subprocess) AND present in the environment."""
    return granted(m, "subprocess", name) and name in present_set

def diagnose(m: dict, present_set, name: str) -> str:
    """Diagnose why `name` is unusable: 'ok'|'need-grant'|'need-install'|'need-both'."""
    g = granted(m, "subprocess", name)
    e = name in present_set
    if g and e:
        return "ok"
    if g and not e:
        return "need-install"   # granted, absent
    if e and not g:
        return "need-grant"     # present, forbidden
    return "need-both"

def capability_precondition(m: dict, present_set, required_names) -> tuple:
    """Return (capable, reason). Incapable if any required name is not usable (U = G ∩ E)."""
    missing = [n for n in required_names if not usable(m, present_set, n)]
    if missing:
        remedies = "; ".join(f"{n}: {diagnose(m, present_set, n)}" for n in missing)
        return (False, f"incapable — required capabilities unusable ({remedies})")
    return (True, "capable")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd RDL && python3 -m pytest tests/test_manifest.py -q`
Expected: PASS (9 passed)

- [ ] **Step 6: Commit** (vcs=none ⇒ logged no-op)

```bash
# vcs=none: not a git repo. Log the skip per C-NOSILENT; do not fail.
echo "SKIP commit: RDL skill dir is not under version control (vcs=none)"
```

---

### Task 2: Base + example manifest data files

**Files:**
- Create: `RDL/rdloop/rdloop.base.toml` (canonical scaffold text, kept in sync with `schema.BASE_MANIFEST`)
- Create: `RDL/references/example-manifest.metavacua.toml`
- Test: `RDL/tests/test_example_manifests.py`

**Interfaces:**
- Consumes: `schema.scaffold`, `schema.validate`, `schema.load` (Task 1).
- Produces: two on-disk manifests validated by the schema.

- [ ] **Step 1: Write the failing test**

```python
# RDL/tests/test_example_manifests.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema

RDL = Path(__file__).resolve().parents[1]

def test_base_toml_matches_scaffold():
    text = (RDL / "rdloop" / "rdloop.base.toml").read_text()
    assert text == schema.scaffold(), "rdloop.base.toml drifted from schema.BASE_MANIFEST"

def test_example_metavacua_validates():
    m = schema.load(RDL / "references" / "example-manifest.metavacua.toml")
    schema.validate(m)

def test_example_metavacua_grants_up_from_floor():
    m = schema.load(RDL / "references" / "example-manifest.metavacua.toml")
    assert m["project"]["vcs"] == "git"
    assert "gh" in m["capabilities"]["subprocess"]
    assert m["issues"]["tracker"] == "github"
    assert any("metavacua" in r for r in m["issues"]["write_repos"])
    assert m["resources"]["memory_budget_mb"] == 6300
    # chrishayuk is read-only: present in read_repos, absent from write_repos
    assert any("chrishayuk" in r for r in m["issues"]["read_repos"])
    assert not any("chrishayuk" in r for r in m["issues"]["write_repos"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd RDL && python3 -m pytest tests/test_example_manifests.py -q`
Expected: FAIL — `FileNotFoundError` for `rdloop.base.toml`

- [ ] **Step 3: Write `rdloop.base.toml`**

Write the exact output of `python3 -c "from rdloop import schema; print(schema.scaffold(), end='')"` to `RDL/rdloop/rdloop.base.toml`:

```bash
cd RDL && python3 -c "from rdloop import schema; open('rdloop/rdloop.base.toml','w').write(schema.scaffold())"
```

- [ ] **Step 4: Write the metavacua example manifest**

```toml
# RDL/references/example-manifest.metavacua.toml
# EXAMPLE ONLY — the historical metavacua environment expressed as explicit grants
# above the least-privilege floor. Illustrative; not the default.

[project]
name = "babel-harness"
target = "x86_64-linux"
docs_dir = "docs/superpowers"
vcs = "git"

[capabilities]
filesystem = ["~/babel-harness", "~/larql", "docs/superpowers"]
network = ["api.github.com", "openrouter.ai"]
subprocess = ["gh", "git", "pi-harness", "larql-probe", "bin/coding-agent", "python3", "pytest", "uv"]
clock = true
random = true
threads = false
gpu = false

[resources]
memory_budget_mb = 6300
serialize_tasks = true

[issues]
tracker = "github"
write_repos = ["metavacua/babel-harness", "metavacua/larql-to-sparql"]
read_repos = ["metavacua/babel-harness", "metavacua/larql-to-sparql", "chrishayuk/larql"]

[dependencies]
standard = "pep621"          # babel-harness is a Python project → PEP 621 pyproject.toml
manifest = "pyproject.toml"

[delegation]
subagent = "pi-harness"

[security]
default_posture = "deny"
write_allowed = ["metavacua/babel-harness", "metavacua/larql-to-sparql"]

[x.graph_context]
vindex = "larql"
scripts = ["scripts/github_graph.py"]

[x.inference]
wrapper = "larql-probe safe -- "
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd RDL && python3 -m pytest tests/test_example_manifests.py -q`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 3: Manifest reference doc

**Files:**
- Create: `RDL/references/manifest.md`
- Test: `RDL/tests/test_manifest_doc.py`

**Interfaces:**
- Consumes: section names from `schema.REQUIRED_SECTIONS`.
- Produces: `references/manifest.md` documenting every section + the skip/prompt rule; referenced by both SKILL bodies (Tasks 4/5).

- [ ] **Step 1: Write the failing test**

```python
# RDL/tests/test_manifest_doc.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema

DOC = Path(__file__).resolve().parents[1] / "references" / "manifest.md"

def test_doc_covers_every_required_section():
    text = DOC.read_text()
    for s in schema.REQUIRED_SECTIONS:
        assert f"[{s}]" in text, f"manifest.md does not document [{s}]"

def test_doc_states_skip_prompt_rule():
    text = DOC.read_text().lower()
    assert "logged skip" in text and "user prompt" in text and "never" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd RDL && python3 -m pytest tests/test_manifest_doc.py -q`
Expected: FAIL — `FileNotFoundError`

- [ ] **Step 3: Write `references/manifest.md`**

```markdown
# The `rdloop.toml` Manifest

The chain requires an `rdloop.toml` manifest. It is discovered by walking up from
the current directory. If none is found, the chain scaffolds a minimal non-trivial
base (`rdloop/rdloop.base.toml`), writes it, and pauses for review — it never runs
on implicit defaults.

## Model: zero ambient authority

Every capability is DENIED unless explicitly granted (WASI Preview 2 / iframe sandbox
allowlist). The default target is a constrained sandbox (`wasm32v1-none`): no network,
filesystem, subprocess, clock, entropy, threads, or GPU is assumed.

## Sections

- `[project]` — `name`, `target`, `docs_dir` (where specs/plans are written),
  `vcs` (`git` or `none`; gates every commit step).
- `[capabilities]` — the GRANT axis (permission). `filesystem`/`network`/`subprocess` are
  allowlists ([] = none); `clock`/`random`/`threads`/`gpu` are booleans (false = denied).
- `[dependencies]` — the REQUIREMENT axis, delegated to a recognized native manifest. `standard`
  (default `cargo`; also `pep621`/`maven`; `custom` = flagged off-list opt-in), `manifest` (the
  native file whose deps are PARSED, e.g. `Cargo.toml`), `toolchain` (e.g. `rust-toolchain.toml`).
  Never re-declare deps here.
- `[resources]` — `memory_budget_mb` (finite, never 0/unlimited), `serialize_tasks`.
- `[issues]` — `tracker` (`github`/`none`), `write_repos`, `read_repos`.
- `[delegation]` — `subagent` (`inline` or a command template).
- `[security]` — `default_posture` (`deny`/`allow`), `write_allowed`.
- `[x]` — forward-compatible extension tables (never validated by the chain).

## Capability = granted AND present (U = G ∩ E)

A capability is USABLE only if it is both granted (`G`, `[capabilities]`) and present in the
environment (`E`, resolved at start). Permission and presence are each necessary and jointly
sufficient. Before any work, the chain computes `U = G ∩ E` and checks the precondition: if
`U = ∅` or a required step's needs are not in `U`, the configuration is **incapable** — halt
with a prompt, never burn effort on it.

## The skip/prompt rule (anti-silent-failure)

A step that needs capability `x` where `x ∉ U` NEVER silently no-ops. Diagnose the axis:

- `x` present but ungranted → **need-grant**;  `x` granted but absent → **need-install**;
  neither → **need-both**.
- **REQUIRED** (either axis missing) → **user prompt + halt** with the axis-specific remedy
  (grant `x` / install `x`). A missing required dependency is NEVER skipped or read as "not needed".
- **OPTIONAL** → **logged skip** that NAMES the disabled feature ("architecture rendering disabled:
  structurizr not resolved"), then continue.

A step must NEVER proceed as though it succeeded (no false-clean). Criticality is declared per
step, never auto-judged.

See `example-manifest.metavacua.toml` for a fully-granted example.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd RDL && python3 -m pytest tests/test_manifest_doc.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 4: De-hardcode `research-phase/SKILL.md`

**Files:**
- Modify: `/home/metavacua/.claude/skills/research-phase/SKILL.md` (steps 0.3–0.6)
- Test: `RDL/tests/test_agnostic_research_phase.py`

**Interfaces:**
- Consumes: `references/manifest.md` (Task 3), the skip/prompt rule, `schema` banned-token list.
- Produces: a `research-phase` body with zero hardcoded project identifiers; each shell-out gated on a manifest capability.

- [ ] **Step 1: Write the failing test**

```python
# RDL/tests/test_agnostic_research_phase.py
from pathlib import Path

RP = Path("/home/metavacua/.claude/skills/research-phase/SKILL.md")
BANNED = ["metavacua", "babel-harness", "larql", "chrishayuk", "pi-harness"]

def test_no_hardcoded_identifiers():
    text = RP.read_text().lower()
    hits = [b for b in BANNED if b in text]
    assert not hits, f"research-phase still hardcodes: {hits}"

def test_git_context_gated_on_vcs():
    text = RP.read_text().lower()
    assert "vcs" in text and "git branch" in text  # git commands now conditional on vcs

def test_toolchain_gated_on_subprocess():
    text = RP.read_text()
    assert "[capabilities].subprocess" in text  # step 0.5 references grants

def test_states_skip_rule():
    text = RP.read_text().lower()
    assert "logged skip" in text or "log a skip" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd RDL && python3 -m pytest tests/test_agnostic_research_phase.py -q`
Expected: FAIL — `test_no_hardcoded_identifiers` (metavacua/larql present at lines 46/54/55/113/116) and the gating asserts fail.

- [ ] **Step 3: Edit Step 0.3** — replace the unconditional git block + metavacua PR line.

Replace the fenced block under `## Step 0.3` (currently `git branch/status/log` + `gh pr list --repo metavacua/babel-harness`) with:

````markdown
```bash
# Gated on [project].vcs. If vcs="none": SKIP git context (log the skip), read files directly.
git branch --show-current   # only if vcs="git"
git status                  # only if vcs="git"
git log --oneline -15       # only if vcs="git"
# Open PRs: only if issues.tracker != "none" AND "gh" is in [capabilities].subprocess,
# iterating [issues].read_repos. Ungranted → logged skip.
```
````

- [ ] **Step 4: Edit Step 0.4** — replace metavacua issue block.

Replace `## Step 0.4 — Check metavacua issues` heading with `## Step 0.4 — Check issue tracker` and its block with:

````markdown
Only if `[issues].tracker != "none"` and `gh` is granted in `[capabilities].subprocess`.
Iterate `[issues].read_repos`; for each repo run `gh issue list --repo <repo> --state open`.
If the tracker is `none` or `gh` is ungranted, this step is **non-critical → logged skip**
("skipped issue check: no tracker/gh grant"), not a silent no-op.
````

- [ ] **Step 5: Edit Step 0.5** — gate the toolchain table.

Insert immediately before the ecosystem table in `## Step 0.5`:

````markdown
Run only the toolchains present in `[capabilities].subprocess`. A toolchain absent from
the grants is **non-critical → logged skip** for that ecosystem ("skipped npm checks:
npm not granted") — never a silent "no dependencies found" (which would be a false-clean).
````

- [ ] **Step 6: Edit Step 0.6** — genericize larql vindex.

Replace the `## Step 0.6` body with:

````markdown
If a graph-context capability is declared under `[x].graph_context` and its scripts are
granted in `[capabilities].subprocess`, query the graph. Otherwise this step is
**non-critical → logged skip**.
````

- [ ] **Step 7: Run test to verify it passes**

Run: `cd RDL && python3 -m pytest tests/test_agnostic_research_phase.py -q`
Expected: PASS (4 passed)

- [ ] **Step 8: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 5: De-hardcode `research-development-loop/SKILL.md` + wire manifest & criticality rule

**Files:**
- Modify: `RDL/SKILL.md` (state label line 22; Phase 3 lines 81–104; Phase 5 lines 158–172; Resource Safety 206–209; Security Constraints 218–223)
- Test: `RDL/tests/test_agnostic_rdl.py`

**Interfaces:**
- Consumes: `references/manifest.md` (Task 3), `example-manifest.metavacua.toml` (Task 2).
- Produces: an RDL body that (a) loads the manifest at start, (b) has zero hardcoded identifiers, (c) states the criticality skip/prompt rule verbatim.

- [ ] **Step 1: Write the failing test**

```python
# RDL/tests/test_agnostic_rdl.py
from pathlib import Path

SK = Path("/home/metavacua/.claude/skills/research-development-loop/SKILL.md")
BANNED = ["metavacua", "babel-harness", "chrishayuk", "pi-harness", "larql",
          "ollama", "bin/coding-agent", "6.3 gb"]

def test_no_hardcoded_identifiers():
    text = SK.read_text().lower()
    hits = [b for b in BANNED if b in text]
    assert not hits, f"RDL SKILL.md still hardcodes: {hits}"

def test_loads_manifest_at_start():
    text = SK.read_text()
    assert "rdloop.toml" in text and "references/manifest.md" in text

def test_states_criticality_rule():
    t = SK.read_text().lower()
    assert "non-critical" in t and "critical" in t
    assert "logged skip" in t and "user prompt" in t
    assert "false-clean" in t or "silently" in t

def test_security_is_manifest_driven():
    text = SK.read_text()
    assert "[security]" in text or "[capabilities]" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd RDL && python3 -m pytest tests/test_agnostic_rdl.py -q`
Expected: FAIL — banned identifiers present; manifest not referenced.

- [ ] **Step 3: Add a manifest preamble** — insert after the opening "Announce at start" line:

````markdown
## Manifest (load first)

Before Phase 0, discover `rdloop.toml` by walking up from cwd. If absent, scaffold the
minimal non-trivial base (`rdloop/rdloop.base.toml`), write it, and pause for user review.
The manifest governs every project-specific behavior below — see `references/manifest.md`.

**Skip/prompt rule (applies to every phase and every step that shells out):** a step whose
required capability is not granted NEVER silently no-ops. If the step is **non-critical**,
log a skip naming the missing grant and continue. If the step is **critical** (the loop
cannot start or correctly continue without it), raise a **user prompt** naming the missing
capability and the exact grant that satisfies it, then halt. Never produce a false-clean.
Criticality is declared per step, not judged algorithmically.
````

- [ ] **Step 4: Edit the state-machine label (line 22).** Change `dev [label="3 Development\n(larql subagent + TDD)"];` to:

```
  dev        [label="3 Development\n(coding subagent + TDD)"];
```

- [ ] **Step 5: Edit Phase 3 Development.** Replace the `pi-harness` command block and delegation table row with manifest-driven text:

````markdown
| Mechanical and well-defined | Delegate to the subagent named in `[delegation].subagent`, if its command is granted in `[capabilities].subprocess` |

Delegation runs `[delegation].subagent` only when granted. If `subagent = "inline"` or the
command is ungranted: mechanical tasks are handled inline (non-critical). A task that
genuinely cannot proceed inline and has no granted subagent is **critical → user prompt**.
After any delegated call, check the tool-call count; zero tool calls = delegation failed =
prerequisite-failure anomaly (surface loudly).

End-to-end demonstrations use `[delegation].demo_runner` if granted; otherwise demonstrate
inline (non-critical, logged).
````

- [ ] **Step 6: Edit Phase 5 issue reconciliation.** Replace the metavacua `gh issue list` block and routing note with:

````markdown
Deferred work is reconciled against the tracker in `[issues]`. If `tracker = "none"` or
`gh` is ungranted, this is **non-critical → logged skip** (record the deferred item in the
paper's limitations section instead). When granted, search before filing: iterate
`[issues].read_repos` with `gh issue search`. File/comment only on repos in
`[issues].write_repos`. A repo in `read_repos` but not `write_repos` is read-only by
construction — no special-case rule needed.
````

- [ ] **Step 7: Edit Resource Safety.** Replace the 6.3 GB / larql-server block with:

````markdown
## Resource Safety

Respect `[resources]`. Never assume system RAM is free: `memory_budget_mb` is the ceiling,
and if `serialize_tasks = true`, run resource-heavy tasks in series, never in parallel.
Any subprocess that launches a server or heavy worker must be granted in
`[capabilities].subprocess`; ungranted → skip/prompt per criticality.
````

- [ ] **Step 8: Edit Security Constraints.** Replace the metavacua/chrishayuk table with:

````markdown
## Security Constraints (non-negotiable)

All writes are governed by the manifest, deny-by-default:

| Action | Allowed scope |
|--------|--------------|
| POST/PATCH/DELETE to a tracker | repos in `[issues].write_repos` only |
| GET from a tracker | repos in `[issues].read_repos` only |
| Filesystem writes / commits / PRs | paths/scopes in `[capabilities].filesystem` + `[security].write_allowed` |
| Anything unlisted | denied (`[security].default_posture = "deny"`) → skip/prompt per criticality |

A resource in a read list but absent from the corresponding write list is read-only by
construction. Any subagent result that violates these grants is discarded, not applied.
````

- [ ] **Step 9: Run test to verify it passes**

Run: `cd RDL && python3 -m pytest tests/test_agnostic_rdl.py -q`
Expected: PASS (4 passed)

- [ ] **Step 10: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 6: Genericize `references/*.md`, relocate metavacua specifics

**Files:**
- Modify: `RDL/references/delegation.md`, `RDL/references/issue-governance.md`, `RDL/references/dependency-exploration.md`, `RDL/references/hooks-architecture.md`
- Test: `RDL/tests/test_agnostic_references.py`

**Interfaces:**
- Consumes: `example-manifest.metavacua.toml` (Task 2) as the new home for specifics.
- Produces: reference docs whose normative text is generic; metavacua/pi-harness appear only in blocks explicitly labelled `Example:`.

- [ ] **Step 1: Write the failing test**

```python
# RDL/tests/test_agnostic_references.py
from pathlib import Path
import re

REFDIR = Path("/home/metavacua/.claude/skills/research-development-loop/references")
BANNED = ["metavacua", "babel-harness", "chrishayuk", "pi-harness", "ollama", "larql"]
FILES = ["delegation.md", "issue-governance.md", "dependency-exploration.md", "hooks-architecture.md"]

def test_specifics_only_under_example_labels():
    for fname in FILES:
        text = (REFDIR / fname).read_text()
        for i, line in enumerate(text.splitlines()):
            low = line.lower()
            if any(b in low for b in BANNED):
                # allowed only on a line that (or whose block) is marked Example:
                assert "example" in low, f"{fname}:{i+1} has a specific outside an Example: {line!r}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd RDL && python3 -m pytest tests/test_agnostic_references.py -q`
Expected: FAIL — specifics on non-Example lines across all four files.

- [ ] **Step 3: Edit `delegation.md`** — replace every `pi-harness`/`ollama` decision line with the generic `[delegation].subagent` / `[capabilities].subprocess` mechanism. Convert any concrete command to an inline `Example:` prefix, e.g.:

```markdown
Delegate mechanical tasks to `[delegation].subagent` when its command is granted in
`[capabilities].subprocess`; otherwise handle inline (non-critical) or prompt (critical).
Example: a fully-granted host might set `subagent = "pi-harness"` with an
`ollama/qwen2.5-coder:7b` local fallback.
```

- [ ] **Step 4: Edit `issue-governance.md`** — replace the metavacua↔larql routing table with generic routing over `[issues].write_repos`, and drop the "never chrishayuk" rule (now the read-only default). Any concrete repo goes behind `Example:`.

- [ ] **Step 5: Edit `dependency-exploration.md`** — prefix the `babel-harness-94485d4.vlp` fixture references and Task #14 lines with `Example:`.

- [ ] **Step 6: Edit `hooks-architecture.md`** — change "dispatch the coding subagent (pi-harness)" to "dispatch the coding subagent (`[delegation].subagent`)".

- [ ] **Step 7: Run test to verify it passes**

Run: `cd RDL && python3 -m pytest tests/test_agnostic_references.py -q`
Expected: PASS (1 passed)

- [ ] **Step 8: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none"
```

---

### Task 7: De-hardcode + extend `evals/evals.json` with the bare-sandbox false-clean guard

**Files:**
- Modify: `RDL/evals/evals.json`
- Test: `RDL/tests/test_evals_agnostic.py`

**Interfaces:**
- Consumes: nothing (self-contained JSON edit).
- Produces: an eval set with no hardcoded repo, plus a new eval asserting the skip/prompt-not-false-clean behavior in a bare sandbox.

- [ ] **Step 1: Write the failing test**

```python
# RDL/tests/test_evals_agnostic.py
import json
from pathlib import Path

EVALS = Path("/home/metavacua/.claude/skills/research-development-loop/evals/evals.json")

def test_evals_parse():
    json.loads(EVALS.read_text())

def test_no_hardcoded_repo_in_evals():
    text = EVALS.read_text().lower()
    for b in ["metavacua/babel-harness", "metavacua/larql-to-sparql"]:
        assert b not in text, f"eval still hardcodes {b}"

def test_bare_sandbox_eval_present():
    data = json.loads(EVALS.read_text())
    names = [e["eval_name"] for e in data["evals"]]
    assert "bare-sandbox-no-false-clean" in names

def test_bare_sandbox_eval_asserts_skip_not_false_clean():
    data = json.loads(EVALS.read_text())
    e = next(e for e in data["evals"] if e["eval_name"] == "bare-sandbox-no-false-clean")
    blob = json.dumps(e).lower()
    assert "logged skip" in blob or "log a skip" in blob
    assert "false-clean" in blob or "false clean" in blob
    assert "incapable" in blob and "halt" in blob  # required-missing halts, not skips
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd RDL && python3 -m pytest tests/test_evals_agnostic.py -q`
Expected: FAIL — `metavacua/babel-harness` present; bare-sandbox eval absent.

- [ ] **Step 3: Edit eval #1** — replace the metavacua-specific assertion. Change the `checks-open-issues` assertion `description` and the `expected_output` clause `check metavacua GitHub issues (step 0.4)` to:

```
"check the issue tracker declared in [issues] (step 0.4), skipping with a logged reason if tracker=none or gh is ungranted"
```
and the assertion:
```json
{ "name": "gates-issue-check-on-manifest", "description": "Step 0.4 consults [issues].tracker and skips (logged) when no tracker/gh grant exists, rather than assuming a specific repo" }
```

- [ ] **Step 4: Append the bare-sandbox eval** to the `evals` array:

```json
{
  "id": 99,
  "eval_name": "bare-sandbox-no-false-clean",
  "prompt": "Run the loop in a directory with no rdloop.toml, no git repo, no gh, and no language toolchains installed. Investigate whether the test suite passes.",
  "expected_output": "The chain must scaffold a minimal non-trivial rdloop.toml and pause. It then resolves capability = granted AND present (U = G ∩ E) and checks the precondition. Because REQUIRED dependencies (the referenced native manifest's deps, and the loop's own required tools) are absent, the loop must declare itself INCAPABLE and HALT with a user prompt naming what to install — it must NOT 'skip everything and continue', and must NEVER report a false-clean (empty git status read as clean tree, or absent toolchains read as 'no dependencies'). OPTIONAL capabilities that are ungranted/absent (issue check 0.4, graph-context 0.6, git context under vcs=none, architecture rendering) emit a logged skip naming the disabled feature. Unusability is diagnosed to its axis (need-grant / need-install / need-both).",
  "assertions": [
    { "name": "scaffolds-manifest-on-absence", "description": "A minimal non-trivial rdloop.toml is scaffolded and the loop pauses for review" },
    { "name": "required-missing-is-incapable-halt", "description": "Absent REQUIRED dependencies make the loop declare itself incapable and halt with an install prompt — it does not skip-and-continue" },
    { "name": "optional-skip-not-false-clean", "description": "Ungranted/absent OPTIONAL capabilities emit a logged skip naming the disabled feature; never a false-clean" },
    { "name": "axis-diagnosis", "description": "Each unusable capability is diagnosed as need-grant / need-install / need-both, not a bare skip" }
  ],
  "files": []
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd RDL && python3 -m pytest tests/test_evals_agnostic.py -q`
Expected: PASS (4 passed)

- [ ] **Step 6: Run the full Plan-1 suite**

Run: `cd RDL && python3 -m pytest tests/ -q`
Expected: PASS (all tasks' tests green)

- [ ] **Step 7: Commit** (vcs=none ⇒ logged no-op)

```bash
echo "SKIP commit: vcs=none — Plan 1 (D-A) complete"
```

---

## Self-Review

**Spec coverage:** C-MANIFEST → T1/T2; C-LEASTPRIV → T1 (`test_scaffold_is_least_privilege`, `test_validate_rejects_unlimited_memory`); C-AGNOSTIC → T4/T5/T6 grep tests; C-NOSILENT/C-CRITICALITY → T5 preamble + T7 bare-sandbox eval; extraction rows 1–13 → T4 (1,2,10,11,12,13), T5 (3,4,5,6,7,8), T6 (9). AC-1 → T1 scaffold + T5 preamble; AC-2/3 → covered by vcs gating in T4/T5. Example manifest (metavacua de-privileged) → T2.

**Placeholder scan:** no TBD/TODO; every edit step shows exact replacement text and a grep/parse test that verifies it.

**Type consistency:** `scaffold`/`validate`/`load`/`granted`/`gate`/`find_manifest` signatures identical across T1–T3 tests. `REQUIRED_SECTIONS` used consistently in T1/T3. Manifest keys (`[capabilities].subprocess`, `[issues].write_repos`, `[project].vcs`) identical across T4–T7.

Gap check: AC-4/5/6 behavior is prose in SKILL bodies (not executable), so it's covered by (a) the `gate()` unit test in T1 and (b) the bare-sandbox eval in T7 — the executable proxy for the prose rule. Acceptable per the design's "skills are eval-graded + machine-checked where possible."
