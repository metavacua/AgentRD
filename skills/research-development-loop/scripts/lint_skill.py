#!/usr/bin/env python3
"""Agent Skills SKILL.md frontmatter linter.

Industry-standard replacement for superpowers:writing-skills / skill-creator as the
RDL Phase-5 skill-authoring gate. Validates SKILL.md YAML frontmatter against the
Agent Skills open format (agentskills.io spec, verified 2026-07-12):

  name        REQUIRED  kebab-case ^[a-z0-9]+(-[a-z0-9]+)*$, <= 64 chars
  description REQUIRED  non-empty, <= 1024 chars (states WHAT + WHEN)
  license     OPTIONAL  string
  (additional keys allowed: allowed-tools, metadata, etc.)

Stdlib-only (the project declares an empty dependency set via PEP 621): frontmatter
is flat single-line `key: value`, so a minimal parser is used instead of PyYAML.
The declarative source of truth is references/skill-frontmatter.schema.json; this
module enforces the same rules in code so the linter has no third-party dependency.

Usage:  python3 lint_skill.py <path/to/SKILL.md> [more...]
Exit 0 iff every file passes; prints one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESC_MAX = 1024


def parse_frontmatter(text: str) -> dict | None:
    """Return the flat frontmatter dict, or None if no `---`-delimited block leads the file."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    meta: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return meta
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return None  # no closing delimiter


def validate_frontmatter(meta: dict) -> list[str]:
    """Return a list of violation strings ([] == valid) per the Agent Skills format."""
    errs: list[str] = []

    name = meta.get("name")
    if name is None:
        errs.append("name: required field missing")
    elif not isinstance(name, str) or not name:
        errs.append("name: must be a non-empty string")
    else:
        if len(name) > NAME_MAX:
            errs.append(f"name: {len(name)} chars exceeds max {NAME_MAX}")
        if not NAME_RE.match(name):
            errs.append(
                f"name: {name!r} is not kebab-case "
                "(lowercase/digits, single hyphens, no leading/trailing/consecutive hyphen)")

    desc = meta.get("description")
    if desc is None:
        errs.append("description: required field missing")
    elif not isinstance(desc, str) or not desc.strip():
        errs.append("description: must be a non-empty string")
    elif len(desc) > DESC_MAX:
        errs.append(f"description: {len(desc)} chars exceeds max {DESC_MAX}")

    return errs


def lint_skill(path) -> list[str]:
    """Lint a SKILL.md file. Returns violation strings ([] == pass)."""
    path = Path(path)
    text = path.read_text()
    meta = parse_frontmatter(text)
    if meta is None:
        return ["frontmatter: no leading `---`-delimited YAML block found"]
    return validate_frontmatter(meta)


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: lint_skill.py <SKILL.md> [more...]", file=sys.stderr)
        return 2
    failed = False
    for arg in argv:
        errs = lint_skill(arg)
        if errs:
            failed = True
            for e in errs:
                print(f"{arg}: {e}")
        else:
            print(f"{arg}: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
