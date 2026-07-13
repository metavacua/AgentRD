# Finding #8 (MCTS audit): validate() must raise ManifestError (not AttributeError) on a
# mistyped section. (Finding #7's write_allowed⊆filesystem subset check was rejected: the
# example manifest is primary evidence they are distinct additive write scopes, not a subset.)
import tomllib
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdloop import schema


def test_validate_rejects_mistyped_section():
    m = tomllib.loads(schema.scaffold())
    m["capabilities"] = "x"  # present but not a table
    with pytest.raises(schema.ManifestError):
        schema.validate(m)


def test_validate_allows_write_allowed_disjoint_from_filesystem():
    # write_allowed is an additive write/commit scope, not a subset of filesystem.
    m = tomllib.loads(schema.scaffold())
    m["capabilities"]["filesystem"] = ["docs"]
    m["security"]["write_allowed"] = ["some-repo"]  # distinct scope — must NOT raise
    schema.validate(m)
