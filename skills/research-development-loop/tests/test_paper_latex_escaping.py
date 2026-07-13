# Regression test for a defect found during this loop's Phase 5: the paper's
# latex.xsl escaped LaTeX specials only in `tex` mode, so bare & % $ # _ in
# <para>/<listitem> body text passed through unescaped and broke pdflatex.
# Requires xsltproc (granted in [capabilities].subprocess).
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest
from _paths import REPO_ROOT

XSL = REPO_ROOT / "papers" / "agent-skills" / "rdl-superpowers-decoupling" / "xsl" / "latex.xsl"

FIXTURE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <article xmlns="http://docbook.org/ns/docbook" version="5.0" xml:lang="en">
      <info><title>T</title></info>
      <section xml:id="s"><title>S</title>
        <para>A &amp; B, 50% off, $5 each, x_y and #1.</para>
      </section>
    </article>
    """)


@pytest.mark.skipif(shutil.which("xsltproc") is None, reason="xsltproc not present")
def test_body_text_latex_specials_are_escaped(tmp_path):
    src = tmp_path / "fixture.xml"
    src.write_text(FIXTURE)
    out = subprocess.run(["xsltproc", str(XSL), str(src)],
                         capture_output=True, text=True, check=True).stdout
    # Every LaTeX special in body text must be escaped.
    for esc in (r"\&", r"\%", r"\$", r"\_", r"\#"):
        assert esc in out, f"body text not escaped: {esc!r} missing from transform output"
    # And no bare (unescaped) ampersand survives: every & must be preceded by a backslash.
    bare_amps = re.findall(r"(?<!\\)&", out)
    assert not bare_amps, f"unescaped ampersand(s) survived the transform: {out!r}"
