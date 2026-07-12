import tomllib
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema

def test_scaffold_parses_as_toml():
    tomllib.loads(schema.scaffold())  # must not raise

def test_scaffold_has_all_required_sections():
    m = tomllib.loads(schema.scaffold())
    for s in schema.REQUIRED_SECTIONS:
        assert s in m, f"scaffold missing [{s}]"

def test_scaffold_is_least_privilege():
    m = tomllib.loads(schema.scaffold())
    caps = m["capabilities"]
    assert caps["filesystem"] == [] and caps["network"] == [] and caps["subprocess"] == []
    assert caps["clock"] is False and caps["gpu"] is False
    assert m["resources"]["memory_budget_mb"] > 0
    assert m["security"]["default_posture"] == "deny"
    assert m["project"]["vcs"] == "none"

def test_validate_rejects_missing_section():
    m = tomllib.loads(schema.scaffold())
    del m["capabilities"]
    with pytest.raises(schema.ManifestError):
        schema.validate(m)

def test_validate_rejects_unlimited_memory():
    m = tomllib.loads(schema.scaffold())
    m["resources"]["memory_budget_mb"] = 0
    with pytest.raises(schema.ManifestError):
        schema.validate(m)

def test_validate_accepts_base():
    schema.validate(tomllib.loads(schema.scaffold()))  # must not raise

def test_gate_run_skip_prompt():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["gh"]
    assert schema.gate(m, "subprocess", "gh", critical=False) == "run"
    assert schema.gate(m, "subprocess", "git", critical=False) == "skip"
    assert schema.gate(m, "subprocess", "git", critical=True) == "prompt"

def test_find_manifest_walks_up(tmp_path):
    (tmp_path / "rdloop.toml").write_text(schema.scaffold())
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert schema.find_manifest(deep) == tmp_path / "rdloop.toml"

def test_find_manifest_absent(tmp_path):
    assert schema.find_manifest(tmp_path) is None

def test_scaffold_has_dependencies_section():
    m = tomllib.loads(schema.scaffold())
    assert "dependencies" in m
    assert m["dependencies"]["standard"] == "cargo"          # restrictive default

def test_validate_rejects_unrecognized_standard():
    m = tomllib.loads(schema.scaffold())
    m["dependencies"]["standard"] = "myhomegrownthing"
    with pytest.raises(schema.ManifestError):
        schema.validate(m)

def test_validate_allows_explicit_custom_optin():
    m = tomllib.loads(schema.scaffold())
    m["dependencies"]["standard"] = "custom"                 # off-list opt-in is allowed (flagged elsewhere)
    schema.validate(m)

def test_parse_native_deps_cargo(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname="x"\n[dependencies]\nserde="1"\ntokio={version="1"}\n')
    assert schema.parse_native_deps("cargo", tmp_path / "Cargo.toml") == {"serde", "tokio"}

def test_diagnose_three_axes():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["git", "python"]      # granted
    present = {"python", "gh"}                                 # python + gh present; gh NOT granted
    assert schema.diagnose(m, present, "python") == "ok"          # granted & present
    assert schema.diagnose(m, present, "git") == "need-install"   # granted, not present
    assert schema.diagnose(m, present, "gh") == "need-grant"      # present, NOT granted
    m2 = tomllib.loads(schema.scaffold())
    assert schema.diagnose(m2, set(), "gh") == "need-both"        # neither granted nor present

def test_usable_is_intersection():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["python"]
    assert schema.usable(m, {"python"}, "python") is True
    assert schema.usable(m, set(), "python") is False        # granted, not present
    assert schema.usable(m, {"git"}, "git") is False         # present, not granted

def test_precondition_incapable_when_required_missing():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["python"]
    ok, reason = schema.capability_precondition(m, present_set=set(), required_names=["python"])
    assert ok is False and "python" in reason               # required dep absent -> incapable

def test_precondition_capable_when_required_present():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["subprocess"] = ["python"]
    ok, _ = schema.capability_precondition(m, present_set={"python"}, required_names=["python"])
    assert ok is True
