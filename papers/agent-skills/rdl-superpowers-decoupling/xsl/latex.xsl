<?xml version="1.0" encoding="UTF-8"?>
<!-- DocBook 5 (subset) -> LaTeX (article class). XSLT 1.0 (xsltproc). Output is text. -->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:d="http://docbook.org/ns/docbook">

  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/d:article">
    <xsl:text>\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{longtable}
\usepackage{xcolor}
\title{</xsl:text><xsl:apply-templates select="d:info/d:title" mode="tex"/><xsl:text>}
\author{</xsl:text><xsl:value-of select="d:info/d:author/d:personname/d:othername"/><xsl:text>}
\date{</xsl:text><xsl:value-of select="d:info/d:pubdate"/><xsl:text>}
\begin{document}
\maketitle
</xsl:text>
    <xsl:if test="d:info/d:abstract">
      <xsl:text>\begin{abstract}
</xsl:text><xsl:apply-templates select="d:info/d:abstract/d:para"/><xsl:text>
\end{abstract}
</xsl:text>
    </xsl:if>
    <xsl:apply-templates select="d:section"/>
    <xsl:text>
\end{document}
</xsl:text>
  </xsl:template>

  <xsl:template match="d:section">
    <xsl:text>
\section{</xsl:text><xsl:apply-templates select="d:title" mode="tex"/><xsl:text>}
</xsl:text>
    <xsl:if test="@condition">
      <xsl:text>\noindent\textcolor{gray}{[</xsl:text><xsl:value-of select="@condition"/><xsl:text>]}\par
</xsl:text>
    </xsl:if>
    <xsl:apply-templates select="*[not(self::d:title)]"/>
  </xsl:template>

  <xsl:template match="d:para"><xsl:apply-templates/><xsl:text>
\par
</xsl:text></xsl:template>

  <xsl:template match="d:itemizedlist"><xsl:text>\begin{itemize}
</xsl:text><xsl:apply-templates select="d:listitem"/><xsl:text>\end{itemize}
</xsl:text></xsl:template>
  <xsl:template match="d:orderedlist"><xsl:text>\begin{enumerate}
</xsl:text><xsl:apply-templates select="d:listitem"/><xsl:text>\end{enumerate}
</xsl:text></xsl:template>
  <xsl:template match="d:listitem"><xsl:text>\item </xsl:text><xsl:apply-templates/></xsl:template>

  <xsl:template match="d:informaltable">
    <xsl:text>\begin{longtable}{p{0.35\textwidth}p{0.55\textwidth}}
\hline
</xsl:text>
    <xsl:for-each select="d:tgroup/d:thead/d:row">
      <xsl:for-each select="d:entry"><xsl:if test="position()&gt;1"><xsl:text> &amp; </xsl:text></xsl:if><xsl:text>\textbf{</xsl:text><xsl:apply-templates mode="tex"/><xsl:text>}</xsl:text></xsl:for-each>
      <xsl:text> \\ \hline
</xsl:text>
    </xsl:for-each>
    <xsl:for-each select="d:tgroup/d:tbody/d:row">
      <xsl:for-each select="d:entry"><xsl:if test="position()&gt;1"><xsl:text> &amp; </xsl:text></xsl:if><xsl:apply-templates mode="tex"/></xsl:for-each>
      <xsl:text> \\ \hline
</xsl:text>
    </xsl:for-each>
    <xsl:text>\end{longtable}
</xsl:text>
  </xsl:template>

  <xsl:template match="d:emphasis[@role='bold']"><xsl:text>\textbf{</xsl:text><xsl:apply-templates/><xsl:text>}</xsl:text></xsl:template>
  <xsl:template match="d:emphasis"><xsl:text>\emph{</xsl:text><xsl:apply-templates/><xsl:text>}</xsl:text></xsl:template>
  <xsl:template match="d:literal|d:tag"><xsl:text>\texttt{</xsl:text><xsl:apply-templates mode="tex"/><xsl:text>}</xsl:text></xsl:template>
  <xsl:template match="d:quote"><xsl:text>``</xsl:text><xsl:apply-templates/><xsl:text>''</xsl:text></xsl:template>

  <!-- Default-mode body text (para, listitem, entry, abstract) must also escape
       LaTeX specials; literal/tag/title switch to tex mode explicitly, so there is
       no double escaping. -->
  <xsl:template match="text()">
    <xsl:call-template name="esc"><xsl:with-param name="s" select="."/></xsl:call-template>
  </xsl:template>

  <!-- tex mode escapes special characters in plain text runs -->
  <xsl:template match="d:title" mode="tex"><xsl:apply-templates mode="tex"/></xsl:template>
  <xsl:template match="text()" mode="tex">
    <xsl:call-template name="esc"><xsl:with-param name="s" select="."/></xsl:call-template>
  </xsl:template>
  <xsl:template match="*" mode="tex"><xsl:apply-templates mode="tex"/></xsl:template>

  <!-- Escape all LaTeX-special characters. Order matters: brace-introducing
       replacements (^ ~) run last so their {} are not re-escaped. -->
  <xsl:template name="esc">
    <xsl:param name="s"/>
    <xsl:variable name="v1"><xsl:call-template name="rep"><xsl:with-param name="t" select="$s"/><xsl:with-param name="f" select="'#'"/><xsl:with-param name="r" select="'\#'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v2"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v1"/><xsl:with-param name="f" select="'%'"/><xsl:with-param name="r" select="'\%'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v3"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v2"/><xsl:with-param name="f" select="'&amp;'"/><xsl:with-param name="r" select="'\&amp;'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v4"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v3"/><xsl:with-param name="f" select="'_'"/><xsl:with-param name="r" select="'\_'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v5"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v4"/><xsl:with-param name="f" select="'$'"/><xsl:with-param name="r" select="'\$'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v6"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v5"/><xsl:with-param name="f" select="'{'"/><xsl:with-param name="r" select="'\{'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v7"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v6"/><xsl:with-param name="f" select="'}'"/><xsl:with-param name="r" select="'\}'"/></xsl:call-template></xsl:variable>
    <xsl:variable name="v8"><xsl:call-template name="rep"><xsl:with-param name="t" select="$v7"/><xsl:with-param name="f" select="'^'"/><xsl:with-param name="r" select="'\textasciicircum{}'"/></xsl:call-template></xsl:variable>
    <xsl:call-template name="rep"><xsl:with-param name="t" select="$v8"/><xsl:with-param name="f" select="'~'"/><xsl:with-param name="r" select="'\textasciitilde{}'"/></xsl:call-template>
  </xsl:template>
  <xsl:template name="rep">
    <xsl:param name="t"/><xsl:param name="f"/><xsl:param name="r"/>
    <xsl:choose>
      <xsl:when test="contains($t,$f)">
        <xsl:value-of select="substring-before($t,$f)"/><xsl:value-of select="$r"/>
        <xsl:call-template name="rep"><xsl:with-param name="t" select="substring-after($t,$f)"/><xsl:with-param name="f" select="$f"/><xsl:with-param name="r" select="$r"/></xsl:call-template>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$t"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
