# Notation Reference

## EARS (Easy Approach to Requirements Syntax) — five patterns
- **Ubiquitous:** `THE <system> SHALL <response>`
- **Event-driven:** `WHEN <trigger> THE <system> SHALL <response>`
- **State-driven:** `WHILE <state> THE <system> SHALL <response>`
- **Unwanted behavior:** `IF <condition> THEN THE <system> SHALL <response>`
- **Optional feature:** `WHERE <feature> THE <system> SHALL <response>`

## RFC 2119 / BCP 14 keywords (normative only in ALL-CAPS, per RFC 8174)
MUST / MUST NOT / REQUIRED / SHALL / SHALL NOT / SHOULD / SHOULD NOT / RECOMMENDED / MAY / OPTIONAL.

## Metadata spine (Dublin Core + Schema.org)
Embed a block with `dc:title`, `dc:creator`, `dc:subject`, `dc:description`, `dc:date`,
`dc:type`, `dc:language`, and a Schema.org `TechArticle`/`SoftwareSourceCode` `@type`.
Phase 5 (scholarly-white-paper) reuses this verbatim.

## MADR decision record shape
Context → Decision → Consequences → Alternatives rejected. One record per decision with ≥2
real alternatives.

## Glut register
`G-n: <the two conflicting claims> — status: open | reconciled(<how>)`. Paraconsistent: a live
contradiction is recorded, not forced to a premature resolution.
