#!/usr/bin/env python3
"""PreToolUse capability gate — routes a Bash command's leading executable through the
`rdl-wasm` witness's `gate()` (the powerless-by-default enforcement authority), realizing
the manifest's deny-by-default as an actual Claude Code permission decision.

Closes MCTS-audit finding #1 / spec §6.1 item (1): the capability model stops being
advisory prose and becomes a runtime gate whose decision is computed by the wasm32v1-none
witness (which itself can do nothing but arithmetic).

SAFE BY DEFAULT: shadow mode (always `allow`, negligible overhead) unless `RDL_ENFORCE=1`,
so it can never brick an interactive session. In enforce mode an ungranted subprocess is
DENIED by the wasm gate; a granted one is allowed.
"""
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


def emit(decision: str, reason: str):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    raise SystemExit(0)


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        emit("allow", "rdl-gate: unreadable input")

    enforce = os.environ.get("RDL_ENFORCE") == "1"
    if not enforce:
        emit("allow", "rdl-gate: shadow mode (set RDL_ENFORCE=1 to enforce)")
    if data.get("tool_name") != "Bash":
        emit("allow", "rdl-gate: non-Bash tool")

    cmd = (data.get("tool_input") or {}).get("command", "")
    exe = ""
    for tok in cmd.strip().split():
        head = tok.split("=", 1)[0]
        if "=" in tok and "/" not in head and not tok.startswith(("-", "/", ".")):
            continue  # skip leading VAR=value assignments
        exe = os.path.basename(tok)
        break
    if not exe:
        emit("allow", "rdl-gate: no executable parsed")

    cwd = Path(data.get("cwd") or os.getcwd())
    manifest = next((d / "rdloop.toml" for d in (cwd, *cwd.parents)
                     if (d / "rdloop.toml").is_file()), None)
    if not manifest:
        emit("allow", "rdl-gate: no rdloop.toml in scope")

    m = tomllib.loads(manifest.read_text())
    granted = exe in (m.get("capabilities", {}).get("subprocess") or [])

    wasm = manifest.parent / "witnesses" / "target" / "wasm32v1-none" / "release" / "rdl_wasm.wasm"
    wasmtime = str(Path.home() / ".cargo" / "bin" / "wasmtime")
    if not Path(wasmtime).exists():
        wasmtime = shutil.which("wasmtime")
    if not (wasm.is_file() and wasmtime):
        emit("allow", f"rdl-gate: wasm witness unavailable; cannot enforce '{exe}' (fail-open)")

    # The wasm gate IS the decision. critical=0 => deny-by-default (gate: 0=run, 1=skip).
    try:
        r = subprocess.run([wasmtime, "run", "--invoke", "gate", str(wasm),
                            "1" if granted else "0", "0"],
                           capture_output=True, text=True, timeout=10)
        code = int(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # pragma: no cover
        emit("allow", f"rdl-gate: gate() error ({e}); fail-open")

    decision = {0: "allow", 1: "deny", 2: "ask"}.get(code, "allow")
    emit(decision, f"rdl-wasm gate('{exe}'): granted={granted} -> {decision} (deny-by-default)")


if __name__ == "__main__":
    main()
