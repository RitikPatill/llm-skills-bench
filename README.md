# LLM Skills Bench

A lightweight, self-hostable evaluation framework for measuring and tracking LLM performance across configurable skill dimensions.

## Why

Every team building on LLMs needs a reproducible answer to: *"Is model X actually better than model Y for our use case?"* Most solutions are either heavyweight research infrastructure (HELM, lm-evaluation-harness) or proprietary cloud dashboards. LLM Skills Bench fills the gap: a hackable, local-first tool you can run in minutes.

## What works now

M3 — eval runner + model adapters:

- `adapters.py`: `ModelAdapter` ABC with `OpenAIAdapter` (`gpt-*`, `o1-*`, `o3-*`), `AnthropicAdapter` (`claude-*`), and `get_adapter()` factory
- `scorers.py`: five scoring functions — `score_exact`, `score_fuzzy`, `score_code_execution`, `score_format_check`, `score_llm_judge` — plus `score_task()` dispatcher
- `runner.py`: `run_benchmark()` — filters catalog, calls model, scores each task, writes timestamped JSON to `./results/`
- `llm-bench run --model gpt-4o --skills coding,reasoning` is fully operational
  - `--results-dir` (default `./results`) and `--judge-model` options added
  - Per-skill summary table on completion; results persisted as timestamped JSON under `./results/`

M2 — skill catalog complete:

- Pydantic v2 `SkillTask` schema (`schema.py`) with `ScoringMethod` and `Difficulty` enums
- `catalog.py` loads and validates all YAML files from `src/llm_skills_bench/skills/`
- 50 benchmark tasks across 5 YAML files:
  - `coding.yaml` — 10 tasks, `code_execution` scoring (sum, palindrome, Fibonacci, …)
  - `reasoning.yaml` — 10 tasks, `fuzzy` + `llm_judge` scoring
  - `knowledge.yaml` — 10 tasks, `fuzzy` scoring with reference answers
  - `instruction_following.yaml` — 10 tasks, `format_check` scoring
  - `tool_use.yaml` — 10 tasks, `format_check` + `fuzzy` scoring
- `llm-bench list` pretty-prints the full catalog as a `rich` table with task count summary

M1 — scaffold:

- Python package (`src/llm_skills_bench/`) installable via `pip install -e .`
- Click CLI with `run`, `serve`, and `list` commands
- `pyproject.toml` with all runtime dependencies pinned
- MIT license, `.gitignore`, `requirements.txt`

## Skills

Five built-in skill dimensions, each configurable via YAML:

| Skill | Scoring Method |
|---|---|
| **Coding** | Sandboxed `subprocess` test-case execution |
| **Reasoning** | LLM-as-judge on multi-step logic and math |
| **Knowledge** | Fuzzy string-match against reference answers |
| **Instruction Following** | Format compliance (JSON validity, word count, list structure) |
| **Tool Use** | Structured output and function-call schema parsing |

## Architecture

```
llm-skills-bench/
├── src/llm_skills_bench/
│   ├── __init__.py
│   ├── cli.py          # Click CLI: run, serve, list
│   ├── schema.py       # Pydantic SkillTask model (M2)
│   ├── catalog.py      # YAML loader (M2)
│   ├── adapters.py     # ModelAdapter ABC + OpenAI/Anthropic + get_adapter() (M3)
│   ├── scorers.py      # exact, fuzzy, code_execution, format_check, llm-judge (M3)
│   ├── runner.py       # run_benchmark(), TaskResult, RunResult (M3)
│   ├── skills/         # YAML skill catalog — 50 tasks (M2)
│   └── dashboard/      # FastAPI + Chart.js server (planned M4)
├── results/            # Timestamped JSON run outputs (written by M3 runner)
└── tests/
    ├── test_scaffold.py   # Package + CLI smoke tests (M1)
    ├── test_catalog.py    # Schema validation + catalog loading (M2)
    └── test_runner.py     # Scorer unit tests + run_benchmark mock integration (M3)
```

```
                ┌──────────────┐
  CLI ─────────▶│  run engine  │──▶ results/*.json
                └──────┬───────┘
                       │
          ┌────────────▼────────────┐
          │     ModelAdapter        │
          │  OpenAI | Anthropic     │
          └─────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │     Skill Catalog       │
          │  YAML ──▶ Task objects  │
          └─────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │      Scorer             │
          │  exact | fuzzy          │
          │  code_execution         │
          │  format_check           │
          │  llm-judge              │
          └─────────────────────────┘

  llm-bench serve ──▶ FastAPI dashboard (radar chart, history, comparison)
```

## Getting Started

```bash
pip install -e .
llm-bench --help
```

### CLI

```bash
# List the full skill catalog (50 tasks across 5 skill dimensions)
llm-bench list

# Filter by a custom skills directory
llm-bench list --skills-dir /path/to/skills

# Run the benchmark (M3)
llm-bench run --model gpt-4o --skills coding,reasoning
llm-bench run --model claude-3-5-sonnet-20241022 --skills knowledge
llm-bench run --model gpt-4o  # all skills
llm-bench run --model gpt-4o --judge-model gpt-4o-mini  # cheaper judge

# Coming in M4:
llm-bench serve --port 8080
```

Set your API key before running:

```bash
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
```

## Roadmap

| Milestone | Status | Description |
|---|---|---|
| M1 | ✅ Done | Scaffold, README, pyproject.toml |
| M2 | ✅ Done | YAML skill catalog (50 tasks), `llm-bench list` |
| M3 | ✅ Done | Model adapters (OpenAI, Anthropic) + `run` command, scorers, JSON results |
| M4 | Planned | FastAPI dashboard: radar chart, run history, comparison |

## License

MIT — see [LICENSE](LICENSE).
