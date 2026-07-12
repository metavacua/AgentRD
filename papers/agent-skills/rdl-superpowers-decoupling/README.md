# Decoupling the RDL Skill Chain from the Superpowers Plugin

Scholarly codification (DocBook 5.x XML canonical source → HTML5 + LaTeX/PDF) of the work that
decoupled the Research-Development-Loop skill chain from the third-party Superpowers plugin,
replacing each idiosyncratic dependency with a verified industry standard.

## Contents

- `src/00-metadata.xml` — Dublin Core metadata block (XIncluded by the articles).
- `src/01-decoupling.xml` — main article: the two couplings, the standards mapping, the recursive
  skill-authoring dependency, the capability manifest, verification.
- `src/02-review.xml` — critical review: skill evaluation, three verified findings (each a defect
  in the chain itself), and the mandatory negative inventory.
- `xsl/html5.xsl`, `xsl/latex.xsl` — XSLT 1.0 transforms (DC `<meta>` + Schema.org JSON-LD +
  finding colour-coding for HTML; article class for LaTeX).
- `schema/custom.rnc` — RELAX NG Compact schema (extends the DocBook 5.0 grammar).
- `Makefile` — `validate` (xmllint + jing + finding-vocabulary), `html`, `latex`, `pdf`.

## Build

```
make validate     # xmllint --relaxng (DocBook 5.0) + jing -c (RELAX NG Compact) + vocab check
make html latex   # generated/*.html, generated/*.tex
make pdf           # generated/*.pdf (optional; needs pdflatex)
```

Toolchain: `xmllint`, `xsltproc`, `jing` (Debian `docbook5-xml`, `jing`), optional `pdflatex`.

## Version note

The scholarly-white-paper skill names DocBook **5.2**, whose RNG is not packaged in Debian
bookworm. Validation here is against the packaged DocBook **5.0** RNG (`docbook5-xml`), the
available baseline; the article content (article/info/section/para/table) is version-agnostic.
See finding 3 in `src/02-review.xml`.

## Findings summary

1. The chain permitted **discretionary deferral** of in-scope work (proportionality used as a skip
   reason) — contradicting its own Rice-correct principle. Repaired + guarded.
2. **Phase 5's toolchain** (DocBook/RELAX NG/XSLT) was never declared in the skill or granted in
   the manifest. Repaired + guarded.
3. The scholarly-white-paper skill's **own example does not validate** against stock DocBook 5.0
   (sibling `<title>` after XIncluded `<info>`). Authored in the validating pattern instead.
