from pathlib import Path

import yaml

from llm_skills_bench.schema import SkillTask

_DEFAULT_SKILLS_DIR = Path(__file__).parent / "skills"


def load_skill_file(path: Path) -> list[SkillTask]:
    """Load and validate a single YAML file. Expects top-level key 'tasks'."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [SkillTask(**task) for task in data["tasks"]]


def load_catalog(skills_dir: Path | None = None) -> list[SkillTask]:
    """Load all *.yaml files from skills_dir, return flat list of SkillTask."""
    if skills_dir is None:
        skills_dir = _DEFAULT_SKILLS_DIR
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")
    tasks: list[SkillTask] = []
    for path in sorted(skills_dir.glob("*.yaml")):
        tasks.extend(load_skill_file(path))
    return tasks
