# Build pipeline for the RDL-superpowers-decoupling scholarly paper.
# Requirements: xmllint (libxml2), xsltproc (libxslt), jing (RELAX NG Compact),
# optionally pdflatex. DocBook 5.0 RNG from Debian docbook5-xml.

RNG   := /usr/share/xml/docbook/schema/rng/5.0/docbookxi.rng
RNC   := schema/custom.rnc
SRCS  := $(wildcard src/0[12]*.xml)
HTML  := $(patsubst src/%.xml,generated/%.html,$(SRCS))
TEX   := $(patsubst src/%.xml,generated/%.tex,$(SRCS))
PDF   := $(patsubst src/%.xml,generated/%.pdf,$(SRCS))

.PHONY: all html latex pdf validate finding-vocab clean
all: validate html latex

validate: finding-vocab
	@for f in $(SRCS); do \
	  echo "xmllint (DocBook 5.0 RNG): $$f"; \
	  xmllint --noout --xinclude --relaxng $(RNG) "$$f" || exit 1; \
	  echo "jing (RELAX NG Compact): $$f"; \
	  jing -c $(RNC) "$$f" || exit 1; \
	done
	@echo "OK: all sources validate."

# Controlled vocabulary for finding conditions (DocBook role/condition are open strings).
finding-vocab:
	@bad=$$(grep -hoE 'condition="[^"]*"' $(SRCS) | sort -u \
	  | grep -vE 'condition="(confirmed|confirmed-with-caveats|split)"' || true); \
	if [ -n "$$bad" ]; then echo "INVALID finding condition(s): $$bad"; exit 1; \
	else echo "OK: finding conditions in controlled vocabulary."; fi

html: $(HTML)
generated/%.html: src/%.xml xsl/html5.xsl | generated
	xsltproc --xinclude xsl/html5.xsl $< > $@

latex: $(TEX)
generated/%.tex: src/%.xml xsl/latex.xsl | generated
	xsltproc --xinclude xsl/latex.xsl $< > $@

pdf: $(PDF)
generated/%.pdf: generated/%.tex
	cd generated && pdflatex -interaction=nonstopmode $(notdir $<) >/dev/null 2>&1 || true

generated:
	mkdir -p generated

clean:
	rm -f generated/*.html generated/*.tex generated/*.pdf generated/*.aux generated/*.log generated/*.out generated/*.toc
