# RDL/tests/test_example_manifests.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema

RDL = Path(__file__).resolve().parents[1]

def test_base_toml_matches_scaffold():
    text = (RDL / "rdloop" / "rdloop.base.toml").read_text()
    assert text == schema.scaffold(), "rdloop.base.toml drifted from schema.BASE_MANIFEST"

def test_example_metavacua_validates():
    m = schema.load(RDL / "references" / "example-manifest.metavacua.toml")
    schema.validate(m)

def test_example_metavacua_grants_up_from_floor():
    m = schema.load(RDL / "references" / "example-manifest.metavacua.toml")
    assert m["project"]["vcs"] == "git"
    assert "gh" in m["capabilities"]["subprocess"]
    assert m["issues"]["tracker"] == "github"
    assert any("metavacua" in r for r in m["issues"]["write_repos"])
    assert m["resources"]["memory_budget_mb"] == 6300
    # chrishayuk is read-only: present in read_repos, absent from write_repos
    assert any("chrishayuk" in r for r in m["issues"]["read_repos"])
    assert not any("chrishayuk" in r for r in m["issues"]["write_repos"])
