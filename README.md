# LLM Skills Bench

> Run configurable skill benchmarks against any OpenAI/Anthropic model, score with LLM-as-judge, and visualize results in a web dashboard.

![demo](demo.gif)

## What it is

LLM Skills Bench is a self-hostable evaluation framework for measuring LLM performance across five skill dimensions: coding, reasoning, knowledge, instruction following, and tool use. Each skill is defined in YAML — prompt template, expected output, and scoring method — so the catalog is fully auditable and extensible without touching Python. Three scoring backends ship out of the box: fuzzy string match, sandboxed subprocess execution for Python problems, and LLM-as-judge for open-ended quality assessment.

The workflow is: run a benchmark from the CLI, get a timestamped JSON result file, open the dashboard to compare runs. There is no database. Results are plain JSON on disk, which means they are easy to version, share, or post-process with any tool.

## Quickstart

```bash
git clone https://github.com/RitikPatill/llm-skills-bench.git
cd llm-skills-bench
pip install -e .

export OPENAI_API_KEY=sk-...        # for OpenAI models
# export ANTHROPIC_API_KEY=sk-ant-... # for Anthropic models

llm-bench run --model gpt-4o --skills coding,reasoning
llm-bench serve --port 8080
```

## Usage

**Running benchmarks**

```bash
# Run all 50 built-in tasks against a model
llm-bench run --model gpt-4o

# Run a subset of skills, use a separate judge model
llm-bench run --model claude-3-5-sonnet-20241022 \
    --skills reasoning,knowledge \
    --judge-model gpt-4o

# List every task in the built-in catalog
llm-bench list

# Validate a custom skill directory before running
llm-bench list --skills-dir ./my_skills
```

After each run, a timestamped JSON file lands in `./results/`. The terminal prints a per-skill score table via Rich.

**Dashboard**

`llm-bench serve` starts a FastAPI server at `http://localhost:8080`. The interface has three panels: a radar chart showing per-skill scores for any selected run, a scrollable run history table, and a side-by-side model comparison view. No login required; it reads directly from the local results directory.

**Adding a custom skill**

Create a YAML file with one or more tasks, each specifying a `prompt_template`, `scoring_method`, and any `metadata` the scorer needs (e.g. `test_code` for `code_execution`, `criteria` for `llm_judge`). Copy it into `src/llm_skills_bench/skills/` and pass the skill name to `--skills`.

## Architecture

```
 CLI (Click)
  │
  ├── run ──▶ Skill Catalog (YAML → SkillTask)
  │               │
  │           ModelAdapter (OpenAI | Anthropic)
  │               │
  │           Scorers (exact | fuzzy | code_execution | format_check | llm_judge)
  │               │
  │           results/<run_id>.json
  │
  └── serve ──▶ FastAPI Dashboard
                    │
                reads results/*.json
```

## Project structure

```
llm-skills-bench/
├── src/llm_skills_bench/
│   ├── cli.py          # Click entry point: run, serve, list
│   ├── schema.py       # Pydantic models: SkillTask, TaskResult, RunResult
│   ├── catalog.py      # YAML loader
│   ├── adapters.py     # ModelAdapter ABC + OpenAI/Anthropic implementations
│   ├── scorers.py      # Five scoring backends
│   ├── runner.py       # Orchestrates a full benchmark run
│   ├── dashboard.py    # FastAPI app + API routes
│   ├── skills/         # Built-in YAML catalog — 50 tasks across 5 skills
│   └── templates/      # Jinja2 HTML for the dashboard
├── assets/
│   └── dashboard.svg   # Dashboard screenshot
├── tests/              # pytest suite: catalog, runner, dashboard, scaffold
├── demo.tape           # VHS script to regenerate demo.gif
└── pyproject.toml      # Package metadata and dependencies
```

## Roadmap

- [ ] Local model support via Ollama (llama.cpp / Mistral / Llama 3)
- [ ] Parallel task execution to reduce wall-clock time on large runs
- [ ] CI integration: compare a run against a baseline and fail on regression
- [ ] Export results as CSV or Markdown for inclusion in reports
- [ ] Dashboard authentication for shared or remote deployments

## License

MIT — see [LICENSE](LICENSE).

---

Built autonomously by [autodev](https://github.com/RitikPatill/autodev),
a multi-agent orchestrator I designed. Each commit in this repo was
authored by me; the implementation work was performed by Sonnet under
the orchestrator's control. Read the orchestrator's README to see how.
