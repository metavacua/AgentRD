# The AgentRD project's OWN manifest must practice what the chain preaches:
# a Python project uses the PEP 621 standard (pyproject.toml), not the `custom`
# last-resort opt-in. Closes Phase-5 finding (c), 2026-07-12.
import sys
from pathlib import Path

REPO = Path("/home/metavacua/AgentRD")
sys.path.insert(0, str(REPO / "skills" / "research-development-loop"))
from rdloop import schema  # noqa: E402


def test_project_manifest_validates():
    schema.validate(schema.load(REPO / "rdloop.toml"))


def test_project_uses_pep621_not_custom():
    m = schema.load(REPO / "rdloop.toml")
    assert m["dependencies"]["standard"] == "pep621"
    assert m["dependencies"]["manifest"] == "pyproject.toml"


def test_pyproject_exists_and_parses_as_native_manifest():
    p = REPO / "pyproject.toml"
    assert p.is_file(), "PEP 621 pyproject.toml missing"
    deps = schema.parse_native_deps("pep621", p)  # must not raise
    assert isinstance(deps, set)


def test_pyproject_configures_pytest_testpaths():
    import tomllib
    data = tomllib.loads((REPO / "pyproject.toml").read_text())
    testpaths = data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("testpaths")
    assert testpaths and "skills" in testpaths
