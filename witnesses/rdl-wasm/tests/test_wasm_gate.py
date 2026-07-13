# Hard-gate proof for the rdl-wasm witness: build to wasm32v1-none, prove ZERO imports
# (zero ambient authority), verify the full export inventory, run the actual .wasm via
# wasmtime, and check the Rust/wasm witness agrees with the Python (schema.py) witness on
# the abstract capability interface. Skips cleanly if the rust/wasm toolchain is absent
# (a grant/presence skip, not a false-clean).
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

CRATE = Path(__file__).resolve().parents[1]                       # witnesses/rdl-wasm
REPO = CRATE.parents[1]                                            # repo root
WASM = CRATE / "target" / "wasm32v1-none" / "release" / "rdl_wasm.wasm"
CARGO_BIN = Path.home() / ".cargo" / "bin"


def _tool(name):
    p = CARGO_BIN / name
    return str(p) if p.exists() else shutil.which(name)


CARGO, WT, WASMTIME = _tool("cargo"), _tool("wasm-tools"), _tool("wasmtime")
ENV = {**os.environ, "PATH": f"{CARGO_BIN}:{os.environ.get('PATH', '')}"}

pytestmark = pytest.mark.skipif(
    not (CARGO and WT and WASMTIME),
    reason="rust/wasm toolchain (cargo, wasm-tools, wasmtime) not granted/present",
)


@pytest.fixture(scope="module")
def wasm():
    r = subprocess.run([CARGO, "build", "--release", "--target", "wasm32v1-none"],
                       cwd=CRATE, env=ENV, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert WASM.is_file()
    return WASM


def _wat(w):
    return subprocess.run([WT, "print", str(w)], capture_output=True, text=True, env=ENV).stdout


def _invoke(w, fn, *args):
    r = subprocess.run([WASMTIME, "run", "--invoke", fn, str(w), *map(str, args)],
                       capture_output=True, text=True, env=ENV)
    assert r.returncode == 0, r.stderr
    return int(r.stdout.strip().splitlines()[-1])


def test_hard_gate_zero_imports(wasm):
    # THE gate: a wasm32v1-none module importing nothing is provably powerless.
    assert "(import" not in _wat(wasm)


def test_full_export_inventory(wasm):
    wat = _wat(wasm)
    for fn in ("usable", "diagnose", "gate", "classify_terminal", "dof_step_ok"):
        assert f'(export "{fn}"' in wat, f"missing interface export {fn}"
    for sym in ("memory", "__data_end", "__heap_base"):   # compiler-emitted default surface
        assert f'(export "{sym}"' in wat, f"missing default cdylib export {sym}"


def test_domain_logic_via_wasmtime(wasm):
    assert (_invoke(wasm, "usable", 1, 1), _invoke(wasm, "usable", 1, 0)) == (1, 0)
    assert _invoke(wasm, "gate", 0, 1) == 2                                   # prompt
    assert _invoke(wasm, "classify_terminal", 1, 0, 0, 0, 0, 0) == 2          # inconsistent
    assert _invoke(wasm, "classify_terminal", 0, 1, 1, 0, 0, 0) == 4          # essential undecidable
    assert _invoke(wasm, "dof_step_ok", 3, 4, 0, 0) == 0                      # DOF-increasing defect
    assert _invoke(wasm, "dof_step_ok", 3, 4, 0, 1) == 1                      # unless it classifies


def test_cross_witness_agreement_with_schema_py(wasm):
    # Two witnesses of the same abstract interface must agree. schema.py (python) vs rdl-wasm (rust).
    import sys
    sys.path.insert(0, str(REPO / "skills" / "research-development-loop"))
    from rdloop import schema
    code2str = {0: "ok", 1: "need-grant", 2: "need-install", 3: "need-both"}
    for granted in (0, 1):
        for present in (0, 1):
            m = tomllib.loads(schema.scaffold())
            m["capabilities"]["subprocess"] = ["git"] if granted else []
            present_set = {"git"} if present else set()
            assert code2str[_invoke(wasm, "diagnose", granted, present)] == \
                schema.diagnose(m, present_set, "git")
            assert bool(_invoke(wasm, "usable", granted, present)) == \
                schema.usable(m, present_set, "git")
