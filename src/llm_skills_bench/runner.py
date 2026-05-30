from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

from llm_skills_bench.scorers import score_task

if TYPE_CHECKING:
    from llm_skills_bench.adapters import ModelAdapter
    from llm_skills_bench.schema import SkillTask


class TaskResult(BaseModel):
    task_id: str
    skill: str
    difficulty: str
    scoring_method: str
    score: float
    response: str
    error: str | None = None


class RunResult(BaseModel):
    run_id: str
    model: str
    timestamp: str
    skills_filter: list[str]
    results: list[TaskResult]
    summary: dict[str, float]


def run_benchmark(
    model: str,
    skills_filter: list[str],
    adapter: "ModelAdapter",
    judge_adapter: "ModelAdapter",
    catalog: list["SkillTask"],
    results_dir: Path = Path("./results"),
) -> RunResult:
    run_id = (
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        f"_{model.replace('/', '_').replace('.', '_')}"
    )
    timestamp = datetime.now(timezone.utc).isoformat()

    # Filter catalog
    if skills_filter:
        lower_filter = [s.lower() for s in skills_filter]
        tasks = [t for t in catalog if t.skill.lower() in lower_filter]
    else:
        tasks = list(catalog)

    results: list[TaskResult] = []
    for task in tasks:
        response = ""
        error = None
        score = 0.0
        try:
            response = adapter.complete(task.prompt_template)
            score = score_task(task, response, judge_adapter=judge_adapter)
        except Exception as e:
            error = str(e)

        results.append(
            TaskResult(
                task_id=task.task_id,
                skill=task.skill,
                difficulty=task.difficulty.value,
                scoring_method=task.scoring_method.value,
                score=score,
                response=response,
                error=error,
            )
        )

    # Per-skill mean
    skill_scores: dict[str, list[float]] = {}
    for r in results:
        skill_scores.setdefault(r.skill, []).append(r.score)
    summary = {skill: sum(scores) / len(scores) for skill, scores in skill_scores.items()}

    run_result = RunResult(
        run_id=run_id,
        model=model,
        timestamp=timestamp,
        skills_filter=skills_filter,
        results=results,
        summary=summary,
    )

    results_dir.mkdir(parents=True, exist_ok=True)
    out_file = results_dir / f"{run_id}.json"
    out_file.write_text(run_result.model_dump_json(indent=2), encoding="utf-8")

    return run_result
