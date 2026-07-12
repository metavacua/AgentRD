# rdloop/schema.py — rdloop.toml manifest: scaffold, find, load, validate, gate.
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
docs_dir = "docs"
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
