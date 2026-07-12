---
name: scholarly-white-paper
description: Use when codifying deep research results, literature reviews, or critical analyses into durable, multi-format scholarly documents. Establishes DocBook 5.2 XML as canonical source with XSLT-derived HTML5 and LaTeX. Applies Dublin Core Terms and Schema.org ScholarlyArticle metadata. Validated by RELAX NG Compact schema.
---

# Scholarly White Paper

Create structured scholarly documents from deep research results, critical reviews, or formal analyses. The canonical source is DocBook 5.2 XML; TeX/PDF and HTML5 are derived outputs, never primary sources.

## When to Use

- Codifying a deep research workflow's output into a permanent document
- Writing a structured critical review with verified findings
- Producing a formal white paper that needs both web (HTML5) and print (PDF) output
- Any document that requires Dublin Core + Schema.org structured metadata

## Folder Structure

Create this structure inside the target repository:

```
papers/<category>/<slug>/
  src/
    00-metadata.xml     Dublin Core + Schema.org (XIncluded by all articles)
    01-<topic>.xml      DocBook 5.2 article (primary content)
    02-<review>.xml     DocBook 5.2 article (review/analysis, if separate)
    bibliography.bib    BibTeX sources
  xsl/
    html5.xsl           DocBook → HTML5 with DC meta tags + Schema.org JSON-LD
    latex.xsl           DocBook → LaTeX (article class)
  schema/
    custom.rnc          RELAX NG Compact schema (extends DocBook 5.2)
  scratch/
    formulas.md         GitHub Markdown for math formulas and reference tables
    notes.md            Session notes, citation gaps, open questions
  generated/            (git-ignored) HTML5, LaTeX, PDF outputs
  Makefile              Build pipeline
  README.md             Usage and findings summary
  .gitignore            Ignore generated/, *.pdf, *.aux, *.log, *.out, *.toc
```

## Canonical Source: DocBook 5.2 XML

Every article file starts with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<article xmlns="http://docbook.org/ns/docbook"
         xmlns:xi="http://www.w3.org/2001/XInclude"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         version="5.2"
         xml:id="slug-here"
         xml:lang="en">

  <xi:include href="00-metadata.xml"/>
  <title>Your Title</title>

  <section xml:id="section-id">
    <title>Section Title</title>
    <para>Content here.</para>
  </section>

</article>
```

## Metadata Block (`00-metadata.xml`)

A standalone `<info>` fragment that all articles XInclude:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<info xmlns="http://docbook.org/ns/docbook"
      xmlns:dc="http://purl.org/dc/terms/"
      xmlns:schema="https://schema.org/">

  <dc:title>Full Document Title</dc:title>
  <dc:creator>Author Name (tool/date)</dc:creator>
  <dc:subject>Keywords; semicolon; separated</dc:subject>
  <dc:description>One-paragraph abstract.</dc:description>
  <dc:publisher>metavacua/Theory (GitHub)</dc:publisher>
  <dc:date>YYYY-MM-DD</dc:date>
  <dc:type>ScholarlyArticle</dc:type>
  <dc:language>en</dc:language>
  <dc:rights>AGPL-3.0-or-later</dc:rights>

  <bibliomisc role="schema-org-jsonld"><![CDATA[
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "name": "Short Title",
  "datePublished": "YYYY-MM-DD",
  "inLanguage": "en",
  "license": "https://www.gnu.org/licenses/agpl-3.0.html"
}
  ]]></bibliomisc>
</info>
```

## Custom Attributes for Critical Review Documents

Finding sections use these attributes on `<section>`:
- `role="finding"` — marks a verified finding section
- `condition="confirmed"` — adversarially confirmed (3-vote majority)
- `condition="confirmed-with-caveats"` — confirmed but context-sensitive
- `condition="split"` — part confirmed, part refuted

The `xsl/html5.xsl` transform renders these with CSS color-coding:
- confirmed → green border
- split → amber border
- confirmed-with-caveats → blue border

## Build Pipeline (Makefile)

```makefile
SRCS      := $(wildcard src/0*.xml)
HTML_OUTS := $(patsubst src/%.xml,generated/%.html,$(SRCS))
TEX_OUTS  := $(patsubst src/%.xml,generated/%.tex,$(SRCS))

.PHONY: all html latex validate clean

all: validate html latex

validate: $(SRCS)
	@for f in $(SRCS); do \
	  xmllint --noout --xinclude \
	    --relaxng https://docbook.org/xml/5.2/rng/docbook.rng "$$f"; \
	done

html: $(HTML_OUTS)
generated/%.html: src/%.xml xsl/html5.xsl | generated
	xsltproc --xinclude xsl/html5.xsl $< > $@

latex: $(TEX_OUTS)
generated/%.tex: src/%.xml xsl/latex.xsl | generated
	xsltproc --xinclude xsl/latex.xsl $< > $@

generated:
	mkdir -p generated

clean:
	rm -f generated/*.html generated/*.tex generated/*.pdf
	rm -f generated/*.aux generated/*.log generated/*.out generated/*.toc
```

Requirements: `xsltproc` (libxslt), `xmllint` (libxml2), optionally `jing` for RELAX NG,
`pdflatex` for PDF.

## RELAX NG Schema (schema/custom.rnc)

Extend DocBook 5.2 with custom `role` and `condition` attribute constraints:

```
namespace db = "http://docbook.org/ns/docbook"

finding-condition = "confirmed" | "confirmed-with-caveats" | "split"

finding-section =
  element db:section {
    attribute xml:id { xsd:NCName },
    attribute role { "finding" },
    attribute condition { finding-condition },
    element db:title { text },
    element db:para { mixed { any* } }+
  }
```

Validate with: `jing -c schema/custom.rnc src/02-critical-review.xml`

## Scratch Files

Use `scratch/formulas.md` (GitHub Markdown) for:
- Mathematical formulas and correspondence tables
- Quick-reference tables (benchmark numbers, taxonomy lookups)
- Anything that would be TeX-heavy in DocBook but readable in Markdown

Use `scratch/notes.md` for:
- Deep research provenance (agent count, token usage)
- Citation gaps found during review
- Open questions for follow-up
- Architecture diagrams in ASCII

## .gitignore for the Folder

```
generated/
*.pdf
*.aux
*.log
*.out
*.toc
```

## Branch and PR Pattern

```bash
git checkout -b claude/SLUG-codification
# ... write all files, commit per logical unit ...
git push -u origin claude/SLUG-codification
gh pr create --title "feat: scholarly codification of SLUG" \
  --body "DocBook 5.2 XML source + XSLT transforms + RELAX NG schema + build pipeline"
```

## Commit Sequence

1. `chore: scaffold <slug> folder structure`
2. `feat: add Dublin Core + Schema.org metadata block`
3. `feat: encode <topic> as DocBook 5.2 XML`
4. `feat: encode critical review with N verified findings as DocBook 5.2 XML`
5. `feat: encode N-repo relevance audit as DocBook 5.2 XML`
6. `feat: add BibTeX bibliography (N sources) and scratch formula/notes files`
7. `feat: add XSLT 1.0 DocBook-to-HTML5 and DocBook-to-LaTeX transforms`
8. `feat: add RELAX NG compact schema and DocBook build Makefile`
9. `feat: add README with build instructions and findings summary`

## Reference Implementation

See `metavacua/Theory` branch `claude/nsam-critical-review-codification`:
`papers/ai_and_agents/principled-agent-architectures-review/`

Deep research workflow output (105 agents, 2,247,194 tokens) was codified into
4 DocBook XML articles, 23 BibTeX sources, 2 XSLT transforms, 1 RELAX NG schema,
and a GNU Make build pipeline in a single session.
