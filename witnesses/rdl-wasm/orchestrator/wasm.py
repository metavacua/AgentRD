"""Thin driver for the rdl-wasm witness via the `wasmtime` CLI.

Used for the security-critical, low-frequency calls — the capability `gate()` and
`classify_terminal()` — so the *enforcement* decisions go through the powerless-by-default
wasm32v1-none module. The hot-loop PUCT is the cross-witness-verified Python equivalent
(see tests/test_wasm_gate.py::test_cross_witness_puct), so we do not subprocess per node.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

CRATE = Path(__file__).resolve().parents[1]
WASM = CRATE / "target" / "wasm32v1-none" / "release" / "rdl_wasm.wasm"
CARGO_BIN = Path.home() / ".cargo" / "bin"


def _tool(name: str):
    p = CARGO_BIN / name
    return str(p) if p.exists() else shutil.which(name)


CARGO, WASMTIME = _tool("cargo"), _tool("wasmtime")
_ENV = {**os.environ, "PATH": f"{CARGO_BIN}:{os.environ.get('PATH', '')}"}


def available() -> bool:
    return bool(CARGO and WASMTIME)


def build() -> None:
    if not WASM.is_file():
        subprocess.run([CARGO, "build", "--release", "--target", "wasm32v1-none"],
                       cwd=CRATE, env=_ENV, check=True, capture_output=True)


def _invoke(fn: str, *args) -> str:
    r = subprocess.run([WASMTIME, "run", "--invoke", fn, str(WASM), *map(str, args)],
                       capture_output=True, text=True, env=_ENV, check=True)
    return r.stdout.strip().splitlines()[-1]


def gate(granted: bool, critical: bool) -> int:
    """0=run, 1=skip, 2=prompt — the wasm capability gate (enforcement authority)."""
    return int(_invoke("gate", int(bool(granted)), int(bool(critical))))


def usable(granted: bool, present: bool) -> int:
    return int(_invoke("usable", int(bool(granted)), int(bool(present))))
