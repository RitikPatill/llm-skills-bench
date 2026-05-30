"""Tests for scorers and run_benchmark — no network calls."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from llm_skills_bench.adapters import ModelAdapter
from llm_skills_bench.runner import RunResult, TaskResult, run_benchmark
from llm_skills_bench.scorers import (
    score_code_execution,
    score_exact,
    score_format_check,
    score_fuzzy,
    score_llm_judge,
)


# ---------------------------------------------------------------------------
# Minimal mock adapter
# ---------------------------------------------------------------------------

class MockAdapter(ModelAdapter):
    def __init__(self, fixed_response: str) -> None:
        self._response = fixed_response

    def complete(self, prompt: str) -> str:
        return self._response


# ---------------------------------------------------------------------------
# score_exact
# ---------------------------------------------------------------------------

def test_score_exact_pass():
    assert score_exact("1991", "1991") == 1.0


def test_score_exact_fail():
    assert score_exact("1992", "1991") == 0.0


def test_score_exact_case_insensitive():
    assert score_exact("Paris", "paris") == 1.0


# ---------------------------------------------------------------------------
# score_fuzzy
# ---------------------------------------------------------------------------

def test_score_fuzzy_pass():
    # Nearly identical strings should pass the default threshold of 80
    assert score_fuzzy("The quick brown fox", "The quick brown fox") == 1.0


def test_score_fuzzy_fail():
    result = score_fuzzy("banana", "The Eiffel Tower is in Paris")
    assert result < 1.0


# ---------------------------------------------------------------------------
# score_code_execution
# ---------------------------------------------------------------------------

def test_score_code_execution_pass():
    code = "def add(a, b):\n    return a + b\n"
    test_code = "assert add(1, 2) == 3\nassert add(-1, 1) == 0\n"
    assert score_code_execution(code, test_code) == 1.0


def test_score_code_execution_fail():
    code = "def add(a, b):\n    return a - b\n"  # wrong implementation
    test_code = "assert add(1, 2) == 3\n"
    assert score_code_execution(code, test_code) == 0.0


def test_score_code_execution_markdown_fence():
    response = "```python\ndef add(a, b):\n    return a + b\n```"
    test_code = "assert add(2, 3) == 5\n"
    assert score_code_execution(response, test_code) == 1.0


# ---------------------------------------------------------------------------
# score_format_check
# ---------------------------------------------------------------------------

def test_score_format_check_json_keys_pass():
    response = json.dumps({"name": "A", "age": 1})
    score = score_format_check(response, {"required_keys": ["name", "age"]})
    assert score == 1.0


def test_score_format_check_json_missing_key():
    response = json.dumps({"name": "A"})
    score = score_format_check(response, {"required_keys": ["name", "age"]})
    assert score < 1.0


def test_score_format_check_word_limit_pass():
    response = " ".join(["word"] * 10)
    score = score_format_check(response, {"max_words": 50})
    assert score == 1.0


def test_score_format_check_word_limit_fail():
    response = " ".join(["word"] * 60)
    score = score_format_check(response, {"max_words": 50})
    assert score == 0.0


# ---------------------------------------------------------------------------
# score_llm_judge
# ---------------------------------------------------------------------------

def test_score_llm_judge_pass():
    adapter = MockAdapter("PASS")
    score = score_llm_judge("42", "What is 6 * 7?", "Correct multiplication", adapter)
    assert score == 1.0


def test_score_llm_judge_fail():
    adapter = MockAdapter("FAIL")
    score = score_llm_judge("99", "What is 6 * 7?", "Correct multiplication", adapter)
    assert score == 0.0


# ---------------------------------------------------------------------------
# run_benchmark integration (all local, no network)
# ---------------------------------------------------------------------------

def _make_catalog():
    from llm_skills_bench.schema import Difficulty, ScoringMethod, SkillTask

    return [
        SkillTask(
            task_id="t001",
            skill="coding",
            prompt_template="Write a function.",
            expected_output=None,
            scoring_method=ScoringMethod.code_execution,
            difficulty=Difficulty.easy,
            metadata={"test_code": "assert True"},
        ),
        SkillTask(
            task_id="t002",
            skill="knowledge",
            prompt_template="Capital of France?",
            expected_output="Paris",
            scoring_method=ScoringMethod.fuzzy,
            difficulty=Difficulty.easy,
        ),
    ]


def test_run_benchmark_mock(tmp_path: Path):
    catalog = _make_catalog()
    adapter = MockAdapter("Paris")
    result = run_benchmark(
        model="mock-model",
        skills_filter=[],
        adapter=adapter,
        judge_adapter=adapter,
        catalog=catalog,
        results_dir=tmp_path,
    )

    assert isinstance(result, RunResult)
    assert len(result.results) == 2
    assert all(isinstance(r, TaskResult) for r in result.results)

    # JSON file should exist
    json_files = list(tmp_path.glob("*.json"))
    assert len(json_files) == 1

    # JSON should be parseable
    data = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert data["model"] == "mock-model"
    assert len(data["results"]) == 2
