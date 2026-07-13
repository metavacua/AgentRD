# The wasm gate wired into a PreToolUse hook (spec §6.1 item 1). Verifies the hook's
# decision is computed by the rdl-wasm gate(): shadow mode always allows (safe); enforce
# mode allows a granted subprocess and DENIES an ungranted one via the wasm.
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from _paths import REPO_ROOT

HOOK = REPO_ROOT / "hooks" / "enforce-capability.py"
CARGO_BIN = Path.home() / ".cargo" / "bin"


def _tool(n):
    p = CARGO_BIN / n
    return str(p) if p.exists() else shutil.which(n)


CARGO, WASMTIME = _tool("cargo"), _tool("wasmtime")
pytestmark = pytest.mark.skipif(not (CARGO and WASMTIME),
                                reason="rust/wasm toolchain not present")
_ENVBASE = {**os.environ, "PATH": f"{CARGO_BIN}:{os.environ.get('PATH', '')}"}


@pytest.fixture(scope="module", autouse=True)
def _wasm():
    wasm = REPO_ROOT / "witnesses" / "target" / "wasm32v1-none" / "release" / "rdl_wasm.wasm"
    if not wasm.is_file():
        subprocess.run([CARGO, "build", "--release", "--target", "wasm32v1-none"],
                       cwd=REPO_ROOT / "witnesses", env=_ENVBASE, check=True, capture_output=True)


def _decide(command, enforce, tool="Bash"):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}, "cwd": str(REPO_ROOT)})
    env = dict(_ENVBASE)
    env.pop("RDL_ENFORCE", None)
    if enforce:
        env["RDL_ENFORCE"] = "1"
    r = subprocess.run(["python3", str(HOOK)], input=payload, capture_output=True, text=True, env=env)
    return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]


def test_shadow_mode_never_blocks():
    assert _decide("rm -rf /", enforce=False) == "allow"          # safe by default


def test_enforce_allows_granted_capability():
    assert _decide("cargo build --release", enforce=True) == "allow"  # cargo IS granted


def test_enforce_denies_ungranted_capability_via_wasm():
    assert _decide("curl http://example.com", enforce=True) == "deny"  # curl NOT granted


def test_enforce_ignores_non_bash():
    assert _decide("anything", enforce=True, tool="Write") == "allow"
