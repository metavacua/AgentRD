# AgentRD

Dedicated project for the Research-Development-Loop (RDL) skill chain.

Members (deployed via symlink into `~/.claude/skills/` for Claude Code discovery):
research-development-loop, research-phase, rdl-brainstorming, rdl-writing-plans,
absence-detection, scholarly-white-paper.

The chain is decoupled from the `superpowers` plugin: it invokes no external plugin skill as a
required step and runs to completion with `superpowers` absent. Each phase's method is an
industry standard — EARS/RFC 2119/C4/MADR (design), WBS + Requirements Traceability Matrix + TDD
(plans), Root-Cause Analysis (debug), Definition of Done + V&V (verify), the Agent Skills open
format + `lint_skill.py` (skill authoring), and GitHub Flow + Conventional Commits (finish).
Superpowers skills remain credited as compatible reference implementations. Each skill's
requirements are elevated to a declared, resolved-up-front manifest (capability = granted ∩ present).
