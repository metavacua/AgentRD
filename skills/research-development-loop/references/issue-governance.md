# Issue Governance and PR/Issue Division Policy

## Core Principle

Durable, cross-branch knowledge → **repository** (specs, ADRs, skills, CLAUDE.md).
Branch-specific decisions and reviews → **PRs and PR comments**.
Tracked and deferred work → **issues and issue comments**.

A one-off PR decision that shouldn't bind future branches belongs in the PR description only — never in a commit message ADR or a spec file.

## Division Table

| Content type | Destination |
|---|---|
| Architecture decision affecting all future branches | Spec file in `{[project].docs_dir}/specs/` → commit to repo |
| Skill definition or improvement | `~/.claude/skills/<name>/SKILL.md` → author per the Agent Skills format, validate with `scripts/lint_skill.py` |
| Implementation approach chosen for this PR | PR description |
| Code suggestion on a specific diff line | PR review comment (inline) |
| Out-of-scope bug found during review | New issue |
| Existing tracked bug this PR fixes | Close via PR body: `Fixes #N` |
| Deferred or blocked work (e.g., B3, B7) | Issue — **check existing issues first** (see below) |
| Known limitation in a scholarly paper | Issue + paper's limitations section (both) |
| One-off PR-level style or naming preference | PR review comment only — never a spec |
| Test fixture or reference data used across PRs | Commit to `tests/fixtures/` |

## Deferred Work Protocol

Before filing a new issue for any deferred or blocked work, search each repo in
`[issues].write_repos` for existing issues (open and, if relevant, closed) covering the
same topic:

```bash
# Search open issues
gh issue list --repo <write-repo> --state open

# Search by keyword
gh issue list --repo <write-repo> --state open | grep -i "<keyword>"
gh issue search "<keyword>" --repo <write-repo>
```

Example: with `[issues].write_repos = ["metavacua/babel-harness", "metavacua/larql-to-sparql"]`, run `gh issue list --repo metavacua/babel-harness --state open`.

Then:

- **Issue exists, open** → add a comment with current findings; do not open a duplicate
- **Issue exists, closed** → reopen with rationale if still relevant; or reference from PR description if minor
- **No issue exists** → file a new issue

### New Issue Format

Title: `<area>: <one-line description>`
Example: `larql: vindex rebuild needed for Q4K attn weights (B7)`

Body must include:
- **Root cause** — what was discovered
- **Blocking condition** — what prevents resolution
- **Workaround or mitigation** currently in effect
- **Related code** — file paths, function names, test seams
- Labels: `deferred` or `blocked` as appropriate

### What Never Goes in Issues

- PR-level style or naming preferences (belong in the PR review)
- One-off build failures already fixed
- Duplicate reports (always search first)
- Transient CI noise with no reproduction path

## Subissues vs. Issue Comments

Use a **subissue** (linked child issue) when:
- The deferred work has two or more independent sub-problems that could be fixed separately
- Different people might fix different parts

Use an **issue comment** when:
- Adding context or new findings to an existing issue
- Linking a PR that partially addresses an issue
- Reporting that a workaround was applied

## Repo Routing for Issues

Route each issue to the repo in `[issues].write_repos` whose subsystem it concerns. If a
single issue spans two write repos, file in **both** — each issue cross-references the
other with a link. Never file, comment on, or close issues in a repo that is not in
`[issues].write_repos` (repos in `[issues].read_repos` only are read-only by default).

Cross-reference format in issue body: `Related: <other-write-repo>#N`.

Example: with `[issues].write_repos = ["metavacua/babel-harness", "metavacua/larql-to-sparql"]`, a bug confined to vindex format goes to `metavacua/larql-to-sparql`, a bug confined to the coding-agent CLI goes to `metavacua/babel-harness`, and `chrishayuk/larql` (read-only) is never written to.
