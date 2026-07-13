# Guards the paraidentity-logics knowledge graph: structural integrity, and the
# honesty invariant — verified publications carry a real source; the curator's
# unpublished cluster stays user-asserted, never laundered into 'verified'.
import sys
from pathlib import Path
from _paths import REPO_ROOT

KB = REPO_ROOT / "docs" / "kb"
sys.path.insert(0, str(KB))
import kb  # noqa: E402

G = kb.load()


def test_graph_validates():
    assert kb.validate(G) == []


def test_every_node_and_edge_has_a_known_tier():
    for n in G["nodes"]:
        assert n["status"] in kb.TIERS
    for e in G["edges"]:
        assert e["status"] in kb.TIERS


def test_verified_publications_have_a_real_source():
    for n in G["nodes"]:
        if n["type"] == "Publication" and n["status"] == "verified":
            assert n.get("source", "").startswith("http"), f"{n['id']} verified w/o source"


def test_zizzi_thesis_present_and_verified():
    z = kb.index(G)["zizzi2010"]
    assert z["status"] == "verified" and "1003.5976" in z["identifier"]


def test_curator_cluster_is_user_asserted_not_verified():
    # The honesty invariant: the organizing cluster and its members that the curator
    # pointed at (unpublished) must NOT be marked verified.
    idx = kb.index(G)
    assert idx["paraidentityCluster"]["status"] == "user-asserted"
    for uid in ("L2q", "Lnq", "popperianLogic"):
        assert idx[uid]["status"] == "user-asserted"


def test_no_invented_domain_only_repository_or_standard_vocab():
    ns = G["namespaces"]
    assert ns["plog"].startswith("https://github.com/metavacua/AgentRD")
    # standard vocabularies keep their real URIs; nothing invented
    assert ns["dcterms"] == "http://purl.org/dc/terms/"
    assert "agentrd.local" not in kb.to_turtle(G)


def test_ntriples_export_is_wellformed():
    nt = kb.to_ntriples(G).strip().splitlines()
    assert nt
    for line in nt:
        assert line.endswith(" ."), f"bad N-Triple: {line}"
        # subject, predicate, object, dot -> at least 4 whitespace-separated tokens
        assert len(line.split(" ", 3)) == 4
    assert all(u in kb.to_ntriples(G) for u in ["github.com/metavacua/AgentRD/paralogic#zizzi2010"])
