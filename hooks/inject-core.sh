#!/usr/bin/env bash
# SessionStart hook: inject the RDL canonical core (invariant + terminal + dispatch)
# into context, so the governing contract is always present — the one leverage
# mechanism, carrying a formal contract rather than prose exhortation.
# Emits Claude Code SessionStart JSON: {hookSpecificOutput:{additionalContext}}.
set -euo pipefail

# CLAUDE_PLUGIN_ROOT is set by Claude Code when run as a plugin hook; fall back to
# the repo/plugin root (parent of this hooks/ dir) so the script is testable standalone.
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

python3 - "$ROOT" <<'PY'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
parts = []
for rel in ("core/invariant.md", "core/terminal.md", "core/dispatch.md"):
    parts.append((root / rel).read_text())
context = (
    "<RDL-CORE priority=\"governing\">\n"
    "The Research-Development-Loop governs this session. R&D reduces degrees of freedom.\n\n"
    + "\n\n".join(parts)
    + "\n</RDL-CORE>"
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}))
PY
