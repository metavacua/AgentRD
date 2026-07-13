#!/usr/bin/env python3
"""Loader / validator / query / RDF-exporter for the paraidentity-logics knowledge graph.

Canonical source of truth: paraidentity-logics.json (node-link graph, stdlib-loadable).
Every node and edge carries an epistemic `status` (verified / user-asserted / user-hypothesis);
provenance is queryable here without any third-party dependency. RDF exports (N-Triples, Turtle)
are generated for interoperability with rdflib / Apache Jena / SPARQL. Entity and vocabulary URIs
are rooted in the repository (no invented domains); dcterms/skos/prov keep their standard URIs.

CLI:
  python3 kb.py validate                 # structural + provenance checks; exit 1 on error
  python3 kb.py status <tier>            # list nodes/edges with an epistemic tier
  python3 kb.py members <cluster-id>     # skos:members of a cluster
  python3 kb.py neighbors <node-id>      # outgoing + incoming edges of a node
  python3 kb.py ntriples                 # emit N-Triples to stdout
  python3 kb.py turtle                   # emit Turtle to stdout
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "paraidentity-logics.json"
TIERS = {"verified", "user-asserted", "user-hypothesis", "training-recall-Q"}
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def load(path=DEFAULT) -> dict:
    return json.loads(Path(path).read_text())


def index(graph: dict) -> dict:
    return {n["id"]: n for n in graph["nodes"]}


def validate(graph: dict) -> list[str]:
    errs: list[str] = []
    ids = index(graph)
    if len(ids) != len(graph["nodes"]):
        errs.append("duplicate node id(s)")
    for n in graph["nodes"]:
        if n.get("status") not in TIERS:
            errs.append(f"node {n['id']}: status {n.get('status')!r} not in {TIERS}")
        if n.get("status") == "verified" and n.get("type") == "Publication" and not n.get("source"):
            errs.append(f"node {n['id']}: verified Publication without a source")
        for w in n.get("witnessedBy", []):
            if w not in ids:
                errs.append(f"node {n['id']}: witnessedBy dangling ref {w!r}")
    for e in graph["edges"]:
        if e.get("status") not in TIERS:
            errs.append(f"edge {e['s']} {e['p']} {e['o']}: bad status {e.get('status')!r}")
        for end in (e["s"], e["o"]):
            if end not in ids:
                errs.append(f"edge references unknown node {end!r}")
    return errs


def members(graph: dict, cluster_id: str) -> list[str]:
    return [e["o"] for e in graph["edges"] if e["s"] == cluster_id and e["p"] == "skos:member"]


def neighbors(graph: dict, node_id: str) -> dict:
    out = [(e["p"], e["o"], e["status"]) for e in graph["edges"] if e["s"] == node_id]
    inc = [(e["s"], e["p"], e["status"]) for e in graph["edges"] if e["o"] == node_id]
    return {"out": out, "in": inc}


def by_status(graph: dict, tier: str) -> dict:
    return {
        "nodes": [n["id"] for n in graph["nodes"] if n.get("status") == tier],
        "edges": [(e["s"], e["p"], e["o"]) for e in graph["edges"] if e.get("status") == tier],
    }


# --- RDF export ------------------------------------------------------------

def _iri(ns: dict, term: str) -> str:
    """Expand a qname or bare node-id to a full IRI. Bare ids live in the plog namespace."""
    if ":" in term and term.split(":", 1)[0] in ns:
        pfx, local = term.split(":", 1)
        return ns[pfx] + local
    return ns["plog"] + term  # bare node id -> repository-rooted entity IRI


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")


def _triples(graph: dict):
    """Yield (subject_qname, predicate_qname, object, is_literal) statements."""
    for n in graph["nodes"]:
        s = n["id"]
        yield s, "rdf:type", f"plog:{n['type']}", False
        yield s, "skos:prefLabel", n["label"], True
        yield s, "plog:status", n["status"], True
        if n.get("source"):
            yield s, "dcterms:source", n["source"], "iri"
        if n.get("date"):
            yield s, "dcterms:date", n["date"], True
        if n.get("identifier"):
            yield s, "dcterms:identifier", n["identifier"], True
        for c in n.get("creator", []):
            yield s, "dcterms:creator", c, True
        for w in n.get("witnessedBy", []):
            yield s, "plog:witnessedBy", w, False
        if n.get("note"):
            yield s, "skos:note", n["note"], True
    # Edge-level provenance stays in the canonical JSON (queryable via kb.py); RDF carries structure.
    for e in graph["edges"]:
        yield e["s"], e["p"], e["o"], False


def to_ntriples(graph: dict) -> str:
    ns = dict(graph["namespaces"]); ns["rdf"] = RDF
    lines = []
    for s, p, o, lit in _triples(graph):
        s_i, p_i = f"<{_iri(ns, s)}>", f"<{_iri(ns, p)}>"
        if lit is True:
            o_t = f'"{_esc(o)}"'
        elif lit == "iri":
            o_t = f"<{o}>"
        else:
            o_t = f"<{_iri(ns, o)}>"
        lines.append(f"{s_i} {p_i} {o_t} .")
    return "\n".join(lines) + "\n"


def to_turtle(graph: dict) -> str:
    ns = dict(graph["namespaces"]); ns["rdf"] = RDF
    head = "".join(f"@prefix {p}: <{u}> .\n" for p, u in ns.items()) + "\n"
    lines = []
    for s, p, o, lit in _triples(graph):
        if lit is True:
            o_t = f'"{_esc(o)}"'
        elif lit == "iri":
            o_t = f"<{o}>"
        else:
            o_t = o if (":" in o and o.split(":", 1)[0] in ns) else f"plog:{o}"
        s_t = s if (":" in s and s.split(":", 1)[0] in ns) else f"plog:{s}"
        lines.append(f"{s_t} {p} {o_t} .")
    return head + "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    g = load()
    cmd = argv[0] if argv else "validate"
    if cmd == "validate":
        errs = validate(g)
        print("\n".join(errs) if errs else f"OK: {len(g['nodes'])} nodes, {len(g['edges'])} edges valid.")
        return 1 if errs else 0
    if cmd == "status" and len(argv) > 1:
        print(json.dumps(by_status(g, argv[1]), indent=2)); return 0
    if cmd == "members" and len(argv) > 1:
        print("\n".join(members(g, argv[1]))); return 0
    if cmd == "neighbors" and len(argv) > 1:
        print(json.dumps(neighbors(g, argv[1]), indent=2)); return 0
    if cmd == "ntriples":
        sys.stdout.write(to_ntriples(g)); return 0
    if cmd == "turtle":
        sys.stdout.write(to_turtle(g)); return 0
    print(__doc__); return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
