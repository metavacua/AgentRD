#!/usr/bin/env python3
"""Agent Skills SKILL.md frontmatter linter.

Industry-standard replacement for superpowers:writing-skills / skill-creator as the
RDL Phase-5 skill-authoring gate. Validates SKILL.md YAML frontmatter against the
Agent Skills open format (agentskills.io spec, verified 2026-07-12):

  name        REQUIRED  kebab-case ^[a-z0-9]+(-[a-z0-9]+)*$, <= 64 chars
  description REQUIRED  non-empty, <= 1024 chars (states WHAT + WHEN)
  license     OPTIONAL  string
  (additional keys allowed: allowed-tools, metadata, etc.)

Frontmatter is parsed with a REAL YAML parser (PyYAML) — a flat key:value parser
silently accepts YAML-invalid frontmatter (e.g. an unquoted `description` with a
colon-space), which the actual skill loader drops entirely so the skill never
triggers. The declarative source of truth is references/skill-frontmatter.schema.json.

Usage:  python3 lint_skill.py <path/to/SKILL.md> [more...]
Exit 0 iff every file passes; prints one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml  # real YAML parser — a flat parser cannot detect invalid-YAML frontmatter

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESC_MAX = 1024
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.S)


def parse_frontmatter(text: str):
    """Parse the leading `---`-delimited YAML frontmatter with a real YAML parser.

    Returns (meta, error): meta is a dict or None; error is a message or None. A
    YAML parse failure is a hard error — the actual loader would silently drop every
    field, so the skill would load with no name/description and never trigger.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "frontmatter: no leading `---`-delimited YAML block found"
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return None, f"frontmatter: invalid YAML ({str(e).splitlines()[0].strip()})"
    if not isinstance(meta, dict):
        return None, "frontmatter: not a YAML mapping"
    return meta, None


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
    text = Path(path).read_text()
    meta, err = parse_frontmatter(text)
    if err:
        return [err]
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
