# LLM Skills Bench

A lightweight, self-hostable evaluation framework for measuring and tracking LLM performance across configurable skill dimensions.

## Why

Every team building on LLMs needs a reproducible answer to: *"Is model X actually better than model Y for our use case?"* Most solutions are either heavyweight research infrastructure (HELM, lm-evaluation-harness) or proprietary cloud dashboards. LLM Skills Bench fills the gap: a hackable, local-first tool you can run in minutes.

## What works now

M1 — scaffold complete:

- Python package (`src/llm_skills_bench/`) installable via `pip install -e .`
- Click CLI with `run`, `serve`, and `list` commands registered (stubs — print "Not implemented yet")
- `pyproject.toml` with all runtime dependencies pinned (`openai`, `anthropic`, `fastapi`, `pyyaml`, `thefuzz`, `rich`, and more)
- MIT license, `.gitignore`, placeholder `requirements.txt`
- Scaffold test suite in `tests/`

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
│   ├── cli.py          # Click CLI: run, serve, list (stubs — M1)
│   ├── adapters/       # OpenAI + Anthropic model adapters (planned M3)
│   ├── skills/         # YAML skill catalog loader (planned M2)
│   ├── scoring/        # exact, fuzzy, exec, llm-judge (planned M2)
│   └── dashboard/      # FastAPI + Chart.js server (planned M4)
├── skills/             # YAML skill definitions (planned M2)
├── results/            # Timestamped JSON run outputs (planned M3)
└── tests/
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
          │  exact | fuzzy | exec   │
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

The commands below are registered and accessible via `--help`. They are stubs in M1 and will be implemented in M2–M3.

```
llm-bench run --model gpt-4o --skills coding,reasoning
llm-bench serve --port 8080
llm-bench list
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
| M2 | Planned | YAML skill catalog + scoring engine (~50 tasks) |
| M3 | Planned | Model adapters (OpenAI, Anthropic) + `run` command |
| M4 | Planned | FastAPI dashboard: radar chart, run history, comparison |

## License

MIT — see [LICENSE](LICENSE).
