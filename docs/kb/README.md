# Paraidentity / parareflexive logics — knowledge graph

A queryable reference graph for the cluster: **logics of evidence (LET/LFI/LFU), paranormal
logics, non-reflexive logics of identity (Schrödinger logics) and of consequence, the qubit
logics `Lq`/`L2q`/`Lnq` (Zizzi), Basic Logic (Sambin), refutational/rejection logics, quantum
logic and the Kochen–Specker/Bell no-go theorems**, and their relation to the substructural
family (non-commutative, non-associative) and (hypothesised) non-monotonic reasoning.

## Files
- **`paraidentity-logics.json`** — canonical source of truth (node-link graph, stdlib-loadable).
- **`kb.py`** — loader / validator / query / RDF exporter (Python stdlib only, no `rdflib`).
- **`paraidentity-logics.ttl`**, **`.nt`** — generated RDF (Turtle, N-Triples) for rdflib / Apache
  Jena / SPARQL. Regenerate with `python3 kb.py turtle > paraidentity-logics.ttl`.

## Epistemic provenance (the point)
Every node and edge carries a `status`:
- **`verified`** — a source was confirmed this session (`source` = real arXiv/DOI URL).
- **`user-asserted`** — the curator's pointer or **unpublished** result; *not* independently
  verified (e.g. `L2q`, `Lnq`, `popperianLogic`, the `paraidentityCluster` itself, the
  Zizzi-2010 triple-tie whose exact statement was not extracted from primary text).
- **`user-hypothesis`** — a conjectured relation (e.g. cluster ↔ non-monotonic reasoning).

Query provenance without laundering it:
```
python3 kb.py validate
python3 kb.py members paraidentityCluster
python3 kb.py neighbors nonReflexiveIdentity
python3 kb.py status user-asserted     # exactly what is NOT yet verified
python3 kb.py turtle | head
```

## URIs
`plog:` (the local vocabulary + entities) is rooted in the repository —
`https://github.com/metavacua/AgentRD/paralogic#`. Only the standard external vocabularies
(`dcterms`, `skos`, `prov`, `rdf`) use their canonical URIs.

## Extending it
Edit `paraidentity-logics.json` only. New verified references need a real `source`; unpublished
curator results stay `user-asserted` until sourced. Re-run `python3 kb.py validate` and regenerate
the RDF. The `test_kb.py` suite enforces the honesty invariant (verified ⇒ real source; the
curator cluster stays user-asserted).
