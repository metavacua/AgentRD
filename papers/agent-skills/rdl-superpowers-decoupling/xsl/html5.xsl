<?xml version="1.0" encoding="UTF-8"?>
<!-- DocBook 5 (subset) -> HTML5, with Dublin Core <meta> tags, Schema.org JSON-LD,
     and CSS colour-coding of finding sections. XSLT 1.0 (xsltproc). -->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:d="http://docbook.org/ns/docbook">

  <xsl:output method="html" encoding="UTF-8" indent="yes"
              doctype-system="about:legacy-compat"/>

  <xsl:template match="/d:article">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title><xsl:value-of select="d:info/d:title"/></title>
        <meta name="DC.title" content="{d:info/d:title}"/>
        <meta name="DC.date" content="{d:info/d:pubdate}"/>
        <meta name="DC.type" content="ScholarlyArticle"/>
        <meta name="DC.language" content="en"/>
        <xsl:for-each select="d:info/d:subjectset/d:subject/d:subjectterm">
          <meta name="DC.subject" content="{.}"/>
        </xsl:for-each>
        <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "name": "<xsl:value-of select="d:info/d:title"/>",
  "datePublished": "<xsl:value-of select="d:info/d:pubdate"/>",
  "inLanguage": "en",
  "license": "https://www.gnu.org/licenses/agpl-3.0.html"
}
        </script>
        <style>
          body{max-width:44rem;margin:2rem auto;padding:0 1rem;font:16px/1.6 system-ui,sans-serif;color:#111}
          h1{font-size:1.7rem;line-height:1.25} h2{font-size:1.25rem;margin-top:2rem}
          code{background:#f4f4f4;padding:.1em .3em;border-radius:3px;font-size:.9em}
          table{border-collapse:collapse;width:100%;margin:1rem 0} td,th{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;vertical-align:top}
          .abstract{font-style:italic;color:#333;border-left:3px solid #999;padding-left:1rem}
          .finding{border-left-width:5px;border-left-style:solid;padding:.2rem 1rem;margin:1.2rem 0;border-radius:0 4px 4px 0;background:#fafafa}
          .confirmed{border-left-color:#2e7d32} .split{border-left-color:#f9a825} .confirmed-with-caveats{border-left-color:#1565c0}
          @media (prefers-color-scheme:dark){body{background:#111;color:#eee}code{background:#222}.finding{background:#1a1a1a}td,th{border-color:#444}}
        </style>
      </head>
      <body>
        <article>
          <h1><xsl:value-of select="d:info/d:title"/></h1>
          <xsl:if test="d:info/d:author">
            <p><em><xsl:value-of select="d:info/d:author/d:personname/d:othername"/></em>
            <xsl:if test="d:info/d:pubdate"> &#183; <xsl:value-of select="d:info/d:pubdate"/></xsl:if></p>
          </xsl:if>
          <xsl:if test="d:info/d:abstract">
            <div class="abstract"><xsl:apply-templates select="d:info/d:abstract/d:para"/></div>
          </xsl:if>
          <xsl:apply-templates select="d:section"/>
        </article>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="d:section">
    <xsl:choose>
      <xsl:when test="@role='finding'">
        <section class="finding {@condition}">
          <h2><xsl:value-of select="d:title"/></h2>
          <xsl:apply-templates select="*[not(self::d:title)]"/>
        </section>
      </xsl:when>
      <xsl:otherwise>
        <section>
          <h2><xsl:value-of select="d:title"/></h2>
          <xsl:apply-templates select="*[not(self::d:title)]"/>
        </section>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="d:para"><p><xsl:apply-templates/></p></xsl:template>
  <xsl:template match="d:itemizedlist"><ul><xsl:apply-templates select="d:listitem"/></ul></xsl:template>
  <xsl:template match="d:orderedlist"><ol><xsl:apply-templates select="d:listitem"/></ol></xsl:template>
  <xsl:template match="d:listitem"><li><xsl:apply-templates/></li></xsl:template>

  <xsl:template match="d:informaltable">
    <table><xsl:apply-templates select="d:tgroup"/></table>
  </xsl:template>
  <xsl:template match="d:tgroup">
    <xsl:if test="d:thead"><thead><xsl:apply-templates select="d:thead/d:row"/></thead></xsl:if>
    <tbody><xsl:apply-templates select="d:tbody/d:row"/></tbody>
  </xsl:template>
  <xsl:template match="d:thead/d:row"><tr><xsl:for-each select="d:entry"><th><xsl:apply-templates/></th></xsl:for-each></tr></xsl:template>
  <xsl:template match="d:tbody/d:row"><tr><xsl:for-each select="d:entry"><td><xsl:apply-templates/></td></xsl:for-each></tr></xsl:template>

  <xsl:template match="d:emphasis[@role='bold']"><strong><xsl:apply-templates/></strong></xsl:template>
  <xsl:template match="d:emphasis"><em><xsl:apply-templates/></em></xsl:template>
  <xsl:template match="d:literal|d:tag"><code><xsl:apply-templates/></code></xsl:template>
  <xsl:template match="d:quote">&#8220;<xsl:apply-templates/>&#8221;</xsl:template>

</xsl:stylesheet>
