# Session notes — provenance & open questions

## Provenance
- Single Claude Opus 4.8 (1M) session, 2026-07-12, driven by the research-development-loop skill.
- Phase 0 web-verified every standard cited (Agent Skills format, Conventional Commits, GitHub
  Flow, ISO/IEC/IEEE 29148, IEEE 1012, ASQ RCA, Scrum DoD) before writing it into a skill.
- Test suite: 54 → 83 passing, zero failures, TDD throughout.

## Validation environment
- Debian bookworm; xmllint (libxml2), xsltproc (libxslt), jing 20220510, docbook5-xml (RNG 5.0),
  pdflatex. DocBook 5.2 RNG not distro-packaged → validated against 5.0 baseline.

## Open questions / follow-ups
- Behavioural proof: run the full RDL loop in a Superpowers-absent runtime and assert completion
  (currently a static/regex proxy only).
- Faithfulness of each standard→method mapping is argued, not machine-checked.
- Linter parses flat YAML frontmatter only; block-scalar `description` would mis-parse silently.
- Consider vendoring the DocBook 5.2 RNG to match the skill's stated target version.
