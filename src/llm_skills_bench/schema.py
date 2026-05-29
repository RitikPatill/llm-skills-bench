from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class ScoringMethod(str, Enum):
    exact = "exact"
    fuzzy = "fuzzy"
    llm_judge = "llm_judge"
    code_execution = "code_execution"
    format_check = "format_check"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SkillTask(BaseModel):
    task_id: str
    skill: str
    prompt_template: str
    expected_output: Optional[str] = None
    scoring_method: ScoringMethod
    difficulty: Difficulty
    tags: list[str] = []
    metadata: dict[str, Any] = {}
