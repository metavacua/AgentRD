# Tests for the Agent Skills frontmatter linter — the industry-standard substitute
# for superpowers:writing-skills / skill-creator (Phase 5 skill-authoring gate).
# Rules verified against agentskills.io spec (2026-07-12): name is kebab
# ^[a-z0-9]+(-[a-z0-9]+)*$, <=64 chars; description required, <=1024 chars.
import json
import sys
from pathlib import Path

RDL = Path("/home/metavacua/.claude/skills/research-development-loop")
sys.path.insert(0, str(RDL / "scripts"))
import lint_skill  # noqa: E402

SCHEMA = RDL / "references" / "skill-frontmatter.schema.json"
CHAIN = ["research-development-loop", "research-phase", "rdl-brainstorming",
         "rdl-writing-plans", "absence-detection", "scholarly-white-paper"]


def _valid():
    return {"name": "my-skill", "description": "Does a thing; use when you need that thing."}


def test_schema_is_valid_json():
    json.loads(SCHEMA.read_text())


def test_valid_frontmatter_passes():
    assert lint_skill.validate_frontmatter(_valid()) == []


def test_name_required():
    m = _valid(); del m["name"]
    assert lint_skill.validate_frontmatter(m)


def test_description_required():
    m = _valid(); del m["description"]
    assert lint_skill.validate_frontmatter(m)


def test_name_rejects_uppercase():
    m = _valid(); m["name"] = "MySkill"
    assert lint_skill.validate_frontmatter(m)


def test_name_rejects_leading_hyphen():
    m = _valid(); m["name"] = "-skill"
    assert lint_skill.validate_frontmatter(m)


def test_name_rejects_trailing_hyphen():
    m = _valid(); m["name"] = "skill-"
    assert lint_skill.validate_frontmatter(m)


def test_name_rejects_consecutive_hyphens():
    m = _valid(); m["name"] = "my--skill"
    assert lint_skill.validate_frontmatter(m)


def test_name_rejects_over_64_chars():
    m = _valid(); m["name"] = "a" * 65
    assert lint_skill.validate_frontmatter(m)


def test_name_accepts_64_chars():
    m = _valid(); m["name"] = "a" * 64
    assert lint_skill.validate_frontmatter(m) == []


def test_description_rejects_over_1024_chars():
    m = _valid(); m["description"] = "x" * 1025
    assert lint_skill.validate_frontmatter(m)


def test_optional_license_allowed():
    m = _valid(); m["license"] = "Apache-2.0"
    assert lint_skill.validate_frontmatter(m) == []


def test_lint_skill_missing_frontmatter_fails(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# no frontmatter here\n")
    assert lint_skill.lint_skill(p)


def test_lint_skill_parses_real_file():
    errs = lint_skill.lint_skill(RDL / "SKILL.md")
    assert errs == [], f"orchestrator SKILL.md failed lint: {errs}"


def test_all_chain_skills_pass_lint():
    base = Path("/home/metavacua/.claude/skills")
    failures = {}
    for name in CHAIN:
        errs = lint_skill.lint_skill(base / name / "SKILL.md")
        if errs:
            failures[name] = errs
    assert not failures, f"chain skills failed Agent Skills lint: {failures}"


def test_rejects_yaml_invalid_frontmatter(tmp_path):
    # A colon-space in an unquoted description is invalid YAML: the real loader
    # drops ALL frontmatter silently (skill won't trigger). The linter MUST catch it.
    p = tmp_path / "SKILL.md"
    p.write_text("---\nname: x\ndescription: The loop is self-correcting: anomalies happen\n---\n# body\n")
    errs = lint_skill.lint_skill(p)
    assert errs, "linter must reject YAML-invalid frontmatter (colon-space plain scalar)"


def test_all_chain_skills_have_yaml_valid_frontmatter():
    import yaml  # real parser, the authority — not the flat fallback
    base = Path("/home/metavacua/.claude/skills")
    bad = {}
    for name in CHAIN:
        fm = (base / name / "SKILL.md").read_text().split("---", 2)[1]
        try:
            d = yaml.safe_load(fm)
            if not (isinstance(d, dict) and d.get("name") and d.get("description")):
                bad[name] = "fields dropped"
        except yaml.YAMLError as e:
            bad[name] = str(e)[:60]
    assert not bad, f"skills with invalid YAML frontmatter (won't trigger): {bad}"
