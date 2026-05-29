from pathlib import Path

import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from llm_skills_bench.catalog import load_catalog, load_skill_file
from llm_skills_bench.cli import main
from llm_skills_bench.schema import Difficulty, ScoringMethod, SkillTask


def test_valid_skill_task():
    task = SkillTask(
        task_id="test_001",
        skill="coding",
        prompt_template="Write a function.",
        scoring_method=ScoringMethod.code_execution,
        difficulty=Difficulty.easy,
    )
    assert task.task_id == "test_001"
    assert task.tags == []
    assert task.metadata == {}


def test_invalid_scoring_method():
    with pytest.raises(ValidationError):
        SkillTask(
            task_id="x",
            skill="coding",
            prompt_template="p",
            scoring_method="invalid",
            difficulty="easy",
        )


def test_invalid_difficulty():
    with pytest.raises(ValidationError):
        SkillTask(
            task_id="x",
            skill="coding",
            prompt_template="p",
            scoring_method="exact",
            difficulty="trivial",
        )


def test_load_skill_file_coding():
    skills_dir = Path(__file__).parent.parent / "src/llm_skills_bench/skills"
    tasks = load_skill_file(skills_dir / "coding.yaml")
    assert len(tasks) == 10
    assert all(t.skill == "coding" for t in tasks)
    assert all(t.scoring_method == ScoringMethod.code_execution for t in tasks)


def test_load_full_catalog():
    tasks = load_catalog()
    assert len(tasks) == 50


def test_task_ids_unique():
    tasks = load_catalog()
    ids = [t.task_id for t in tasks]
    assert len(ids) == len(set(ids)), "Duplicate task_ids found"


def test_cli_list():
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "coding" in result.output
    assert "Total:" in result.output
