# Dependency Exploration Reference

## GitHub Dependency Graph API (2026)

All endpoints require `Contents: read` permission. For public repos, no auth needed.

```bash
# Full SBOM in SPDX JSON (complete dependency list + versions + licenses)
gh api /repos/{owner}/{repo}/dependency-graph/sbom

# Async SBOM generation (for large repos; returns UUID, poll with fetch-report)
gh api /repos/{owner}/{repo}/dependency-graph/sbom/generate-report
gh api /repos/{owner}/{repo}/dependency-graph/sbom/fetch-report/{uuid}

# Dependency diff between two refs (added/removed packages, vulnerabilities)
gh api /repos/{owner}/{repo}/dependency-graph/compare/{base}...{head}

# Dependency submission API (for ecosystems not auto-detected, e.g. Gradle)
# POST body: {version, sha, ref, job, detector, scanned, manifests, metadata}
gh api /repos/{owner}/{repo}/dependency-graph/snapshots --method POST --input snapshot.json

# Dependabot alerts — list vulnerabilities in current deps
gh api /repos/{owner}/{repo}/dependabot/alerts
gh api /repos/{owner}/{repo}/dependabot/alerts/{alert_number}       # single alert detail
gh api /orgs/{org}/dependabot/alerts                                 # org-wide view
```

## Supported Ecosystems (GitHub auto-detects from manifest files)

| Ecosystem | Language(s) | Manifest files |
|---|---|---|
| Cargo | Rust | `Cargo.lock` |
| npm | JavaScript | `package-lock.json` |
| pnpm | JavaScript | `pnpm-lock.yaml` |
| Yarn | JavaScript | `yarn.lock` |
| pip | Python | `requirements.txt`, `pipfile.lock` |
| Poetry | Python | `poetry.lock` |
| Go modules | Go | `go.mod` |
| Composer | PHP | `composer.lock` |
| NuGet | C#, F#, VB, C++ | `.csproj`, `.vbproj`, `.nuspec` |
| RubyGems | Ruby | `Gemfile.lock` |
| Maven | Java, Scala | `pom.xml` |
| Gradle | Java | dependency submission API only |
| Swift PM | Swift | `Package.resolved` |
| Bazel | Starlark | `MODULE.bazel`, `WORKSPACE` |
| Deno | TypeScript, JS | `deno.lock` |
| pub | Dart | `pubspec.lock` |
| OpenTofu | HCL | `.terraform.lock.hcl` |
| GitHub Actions | YAML | `.yml`, `.yaml` in `.github/workflows/` |
| Julia | Julia | `Manifest.toml` |

If a manifest file is present in the repo, GitHub parses it automatically. For ecosystems not in this list, use the dependency submission API to push a snapshot programmatically.

## Local Dependency Commands (per ecosystem)

Use these when the GitHub graph is unavailable or when you need transitive depth that SBOM doesn't show.

### Rust / Cargo
```bash
cargo tree                          # full tree, transitive
cargo tree --duplicates             # find version conflicts
cargo tree -e features              # include feature flags
cargo metadata --format-version 1  # machine-readable JSON
```

### Python / pip
```bash
pipdeptree                          # tree view (install: pip install pipdeptree)
pipdeptree --reverse -p <package>   # what depends on <package>?
pip show <package>                  # single package info + Requires/Required-by
poetry show --tree                  # if using Poetry
uv pip tree                         # if using uv
```

### JavaScript / Node
```bash
npm ls --all                        # full dependency tree
npm ls <package>                    # why is <package> installed?
npm why <package>                   # npm v8+
yarn why <package>                  # Yarn
npx depcruise --include-only '^src' src  # structural import graph
```

### Go
```bash
go mod graph                        # all edges in module graph
go mod why <module>                 # shortest import path to <module>
go list -m all                      # all module versions
go list -json -deps ./...           # per-package dependency JSON
```

### Rust / system
```bash
ldd <binary>                        # shared library deps (Linux)
readelf -d <binary>                 # ELF dynamic section
objdump -p <binary> | grep NEEDED   # same, different format
```

### Java / Maven
```bash
mvn dependency:tree                 # full tree
mvn dependency:tree -Dincludes=<groupId>:<artifactId>  # filter
```

### Shell / Bash
```bash
grep -rn '^source\|^\. ' --include="*.sh" .   # source/. includes
grep -rn 'export\|readonly' --include="*.sh" . # env var definitions
```

## Task-Level Dependency Analysis

For determining task execution order:

```
For each pair of tasks (A, B):
  - Does task A create a file that task B reads?       → A before B
  - Does task A define a function that task B tests?   → A before B  
  - Does task A set an env var that task B uses?       → A before B
  - Does task A write a fixture that task B uses?      → A before B
  - None of the above?                                 → independent; parallelizable

Topological sort of the dependency graph = correct execution order.
Independent tasks = pick whichever reduces the most risk or unblocks the most downstream work.
```

### Applied example: two tasks, one a fixture producer

Given a pair of tasks where one adds a test and the other pre-computes a fixture the test
might read, check whether the fixture-producing task's output feeds into the test:

```bash
grep -n "<fixture-name>" tests/*.bash
```

If yes → the fixture-producing task runs first. If no → the tasks are independent; do
whichever is less risky first.

Example: Task #13 adds a `--remote` integration test for `_fetch_remote_triples()`; Task #14 pre-computes and commits `tests/fixtures/babel-harness-94485d4.vlp`.

Example: `grep -n "94485d4\|\.vlp" tests/test-larql-graft.bash tests/test-coding-agent.bash` shows #14's fixture feeds #13's test, so #14 runs before #13.

## GitHub Actions: Dependency Review

`actions/dependency-review-action` — runs on PRs, structured JSON outputs:
- `dependency-changes` — all added/removed packages
- `vulnerable-changes` — packages with known CVEs (severity: low/moderate/high/critical)
- `invalid-license-changes` — SPDX non-compliant licenses
- `denied-changes` — against a custom allowlist/denylist

Use for pre-merge dependency audits in CI. Results queryable via `gh run view` after the action completes.

## SBOM Formats

GitHub exports in **SPDX JSON** (primary) and **CycloneDX** (also supported). Both are compatible with scanning tools:
- `syft` — generates SBOMs from images and directories
- `grype` — vulnerability scanning against an SBOM
- `trivy` — combined SBOM generation + vulnerability scan

CycloneDX 1.6+ supports ML-BOM, CBOM (cryptography), HBOM (hardware) in addition to standard software SBOM.

## SBOM Parsing (SPDX JSON)

GitHub's SBOM uses SPDX 2.3 JSON format. Key fields:

```python
import json, subprocess
sbom = json.loads(subprocess.check_output(
    ["gh", "api", f"/repos/{owner}/{repo}/dependency-graph/sbom"]
))
for pkg in sbom["sbom"]["packages"]:
    print(pkg["name"], pkg.get("versionInfo"), pkg.get("licenseConcluded"))
```

Tools that consume SPDX: `spdx-tools`, `syft`, `grype` (vulnerability scanning).
CycloneDX format is also widely used but GitHub's native export is SPDX.

## Formal Foundations: Logic of Evidence (Gaps and Gluts)

The gap/glut distinction used in Step 0.7 is grounded in the Logic of Formal Inconsistency (LFI) and the Logic of Evidence, developed by Carnielli, Coniglio, and Marcos:

- **Gap** (⊬ P, ⊬ ¬P): underdetermined — insufficient evidence to derive either side. Trigger: gather more evidence (micro-cycle research call).
- **Glut** (⊢ P, ⊢ ¬P): overdetermined by contradictory evidence — classical inference is blocked (explosion would trivialize). Trigger: inconsistency analysis — identify which evidence stream is defeasible; the exposed axiom becomes an E or Q entry.

Key references:
- Carnielli, W., Coniglio, M.E., and Marcos, J. (2007). "Logics of Formal Inconsistency." *Handbook of Philosophical Logic*, Vol. 14, Springer.
- Carnielli, W. and Rodrigues, A. (2019). "An epistemic approach to paraconsistency: a logic of evidence and truth." *Synthese* 196:3789–3813.

In practice: a glut in research is analogous to the Root-Cause-Analysis rule "3+ failed fixes → question the architecture." The contradiction is not noise — it is a signal that an axiom of the surrounding system is false.
