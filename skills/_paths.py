from pathlib import Path
SKILLS_ROOT = Path(__file__).resolve().parent          # .../AgentRD/skills
REPO_ROOT = SKILLS_ROOT.parent                          # .../AgentRD
def skill_dir(name): return SKILLS_ROOT / name
def read_skill(name): return (SKILLS_ROOT / name / "SKILL.md").read_text()
