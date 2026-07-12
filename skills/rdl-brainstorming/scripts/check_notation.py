# BRAIN/scripts/check_notation.py — machine-checkable notation rules.
import re

EARS = {
    "event":      re.compile(r"\bWHEN\b.+\bTHE\b.+\bSHALL\b", re.S),
    "state":      re.compile(r"\bWHILE\b.+\bTHE\b.+\bSHALL\b", re.S),
    "unwanted":   re.compile(r"\bIF\b.+\bTHEN\b.+\bSHALL\b", re.S),
    "optional":   re.compile(r"\bWHERE\b.+\bTHE\b.+\bSHALL\b", re.S),
    "ubiquitous": re.compile(r"\bTHE\b.+\bSHALL\b", re.S),
}
# Keyword-led patterns are checked before the catch-all ubiquitous pattern.
_ORDER = ("event", "state", "unwanted", "optional", "ubiquitous")

def classify_ears(clause: str):
    """Return the EARS pattern name for `clause`, or None if it is not EARS."""
    for name in _ORDER:
        if EARS[name].search(clause):
            return name
    return None

def is_ears(clause: str) -> bool:
    return classify_ears(clause) is not None

RFC2119 = ["MUST NOT", "MUST", "SHALL NOT", "SHALL", "SHOULD NOT", "SHOULD",
           "REQUIRED", "RECOMMENDED", "MAY", "OPTIONAL"]

def normative_keywords(text: str):
    """Return RFC 2119 keywords that appear in ALL-CAPS (normative per RFC 8174)."""
    found = []
    for kw in RFC2119:
        # case-sensitive: uppercase kw only matches uppercase in text
        if re.search(r"(?<![A-Za-z])" + re.escape(kw) + r"(?![A-Za-z])", text):
            found.append(kw)
    return found

def arch_section_required(element_count: int) -> bool:
    """Decidable content-gate: architecture/C4 view required iff >=2 model elements."""
    return element_count >= 2

def adr_required(alt_count: int) -> bool:
    """Decidable content-gate: an ADR record required iff a decision has >=2 alternatives."""
    return alt_count >= 2

def structurizr_action(usable_structurizr: bool) -> str:
    """Map usability (granted AND present — computed via Plan-1 schema.usable) to an action.
    'render' iff usable; else an OPTIONAL-dependency skip that names the disabled feature.
    Never a silent no-op; the .dsl source is authored either way."""
    return "render" if usable_structurizr else "skip:architecture-rendering-disabled"

def plan_task_cites_ac(task_text: str, valid_acs) -> bool:
    """True iff the task cites >=1 AC-n and every cited AC exists in valid_acs."""
    cited = set(re.findall(r"\bAC-\d+\b", task_text))
    return bool(cited) and cited.issubset(set(valid_acs))
