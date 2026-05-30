from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_skills_bench.adapters import ModelAdapter
    from llm_skills_bench.schema import SkillTask


def score_exact(response: str, expected: str) -> float:
    return 1.0 if response.strip().lower() == expected.strip().lower() else 0.0


def score_fuzzy(response: str, expected: str, threshold: int = 80) -> float:
    from thefuzz import fuzz

    ratio = fuzz.partial_ratio(response.strip(), expected.strip())
    return 1.0 if ratio >= threshold else ratio / 100.0


def _extract_code(response: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1)
    return response


def score_code_execution(response: str, test_code: str, timeout: int = 10) -> float:
    code = _extract_code(response)
    combined = code.rstrip() + "\n" + test_code
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(combined)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            timeout=timeout,
        )
        return 1.0 if result.returncode == 0 else 0.0
    except subprocess.TimeoutExpired:
        return 0.0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def score_format_check(response: str, metadata: dict) -> float:
    # JSON keys check
    if "required_keys" in metadata or "required_type" in metadata:
        text = response.strip()
        # strip markdown fences
        fence_match = re.search(r"```(?:json)?\n?(.*?)```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return 0.0
        required_keys = metadata.get("required_keys", [])
        if required_keys:
            present = sum(1 for k in required_keys if k in parsed)
            return present / len(required_keys)
        return 1.0

    # Word limit check
    if "max_words" in metadata:
        word_count = len(response.split())
        return 1.0 if word_count <= metadata["max_words"] else 0.0

    # Words starting with a letter
    if "expected_count" in metadata and "starting_letter" in metadata:
        letter = metadata["starting_letter"].lower()
        words = [w for w in response.split() if w.lower().startswith(letter)]
        expected = metadata["expected_count"]
        return 1.0 if len(words) >= expected else len(words) / max(expected, 1)

    # Numbered list items
    if "expected_count" in metadata:
        lines = re.findall(r"^\d+[.)]\s", response, re.MULTILINE)
        expected = metadata["expected_count"]
        return 1.0 if len(lines) >= expected else len(lines) / max(expected, 1)

    # Table structure
    if "expected_columns" in metadata or "expected_rows" in metadata:
        rows = [
            line
            for line in response.splitlines()
            if "|" in line and not re.match(r"^\s*\|[-| ]+\|\s*$", line)
        ]
        if "expected_rows" in metadata:
            expected = metadata["expected_rows"]
            return 1.0 if len(rows) >= expected else len(rows) / max(expected, 1)
        if "expected_columns" in metadata:
            if rows:
                cols = len([c for c in rows[0].split("|") if c.strip()])
                expected = metadata["expected_columns"]
                return 1.0 if cols >= expected else cols / max(expected, 1)
        return 1.0

    # Uppercase transform
    if metadata.get("transform") == "uppercase":
        text = response.strip()
        return 1.0 if text == text.upper() else 0.0

    # Haiku / syllable pattern — best-effort: check 3 lines present
    if "syllable_pattern" in metadata:
        lines = [l for l in response.strip().splitlines() if l.strip()]
        return 1.0 if len(lines) >= 3 else 0.0

    # No recognizable constraint
    return 1.0


def score_llm_judge(
    response: str,
    task_prompt: str,
    criteria: str,
    adapter: "ModelAdapter",
) -> float:
    judge_prompt = (
        f"You are a grader. Task: {task_prompt}\n"
        f"Model response: {response}\n"
        f"Criteria: {criteria}\n"
        "Reply with exactly one word: PASS or FAIL."
    )
    judgment = adapter.complete(judge_prompt)
    return 1.0 if "PASS" in judgment.upper() else 0.0


def score_task(
    task: "SkillTask",
    response: str,
    judge_adapter: "ModelAdapter | None" = None,
) -> float:
    from llm_skills_bench.schema import ScoringMethod

    method = task.scoring_method

    if method == ScoringMethod.exact:
        return score_exact(response, task.expected_output or "")

    if method == ScoringMethod.fuzzy:
        return score_fuzzy(response, task.expected_output or "")

    if method == ScoringMethod.code_execution:
        test_code = task.metadata.get("test_code", "")
        return score_code_execution(response, test_code)

    if method == ScoringMethod.format_check:
        return score_format_check(response, task.metadata)

    if method == ScoringMethod.llm_judge:
        if judge_adapter is None:
            raise ValueError("judge_adapter is required for llm_judge scoring")
        criteria = task.metadata.get("criteria", "The response is correct and helpful.")
        return score_llm_judge(response, task.prompt_template, criteria, judge_adapter)

    raise ValueError(f"Unknown scoring method: {method}")
