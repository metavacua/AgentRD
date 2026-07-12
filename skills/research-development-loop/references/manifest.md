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
