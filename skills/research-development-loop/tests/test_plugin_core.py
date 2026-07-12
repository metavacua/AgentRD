# TDD for the RDL plugin packaging + injected canonical core (spec:
# docs/specs/2026-07-12-rdl-canonical-core.md). Verified against how real plugins
# wire hooks: .claude-plugin/plugin.json + hooks/hooks.json (SessionStart), the
# superpowers pattern. The hook injection is tested BEHAVIORALLY (run the script,
# parse its JSON), not just structurally.
import json
import subprocess
from pathlib import Path

REPO = Path("/home/metavacua/AgentRD")
PLUGIN_JSON = REPO / ".claude-plugin" / "plugin.json"
HOOKS_JSON = REPO / "hooks" / "hooks.json"
INJECT = REPO / "hooks" / "inject-core.sh"
CORE = REPO / "core"


def test_plugin_manifest_valid():
    m = json.loads(PLUGIN_JSON.read_text())
    assert m["name"] == "rdl"
    assert "version" in m and "description" in m


def test_hooks_json_declares_sessionstart_injection():
    h = json.loads(HOOKS_JSON.read_text())
    ss = h["hooks"]["SessionStart"]
    assert ss[0]["matcher"] == "startup|clear|compact"
    cmd = ss[0]["hooks"][0]
    assert cmd["type"] == "command"
    assert "inject-core.sh" in cmd["command"]
    assert "${CLAUDE_PLUGIN_ROOT}" in cmd["command"]  # portable root, like superpowers
    assert cmd["async"] is False


def test_inject_script_executable():
    assert INJECT.exists()
    assert INJECT.stat().st_mode & 0o111, "inject-core.sh must be executable"


def test_core_files_exist():
    for f in ("invariant.md", "terminal.md", "dispatch.md"):
        assert (CORE / f).is_file(), f"core/{f} missing"


def test_terminal_has_all_five_classes():
    t = (CORE / "terminal.md").read_text().lower()
    assert "determined" in t
    assert "feasible" in t and "optim" in t
    assert "inconsistent" in t or "infeasible" in t
    assert "non-essential" in t and "essential" in t  # the two undecidability rows


def test_invariant_states_dof_reduction():
    inv = (CORE / "invariant.md").read_text().lower()
    assert "degrees of freedom" in inv or "dof" in inv


def test_dispatch_is_adaptive_not_hardcoded():
    d = (CORE / "dispatch.md").read_text().lower()
    assert "available" in d and "bind" in d
    assert "superpowers" in d  # named as ONE admissible binding, not a dependency
    assert "record" in d       # binding must be recorded for reproducibility


def test_hook_injection_emits_core_behaviorally():
    # Run the actual injection script (no CLAUDE_PLUGIN_ROOT -> falls back to repo root)
    # and assert it emits valid SessionStart JSON carrying the core.
    out = subprocess.run(["bash", str(INJECT)], capture_output=True, text=True, check=True).stdout
    payload = json.loads(out)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    low = ctx.lower()
    assert "degrees of freedom" in low          # invariant injected
    assert "determined" in low and "essential" in low  # terminal classification injected
    assert "bind" in low                         # dispatch injected
