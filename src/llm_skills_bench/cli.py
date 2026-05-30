from pathlib import Path

import click
from rich import print as rprint
from rich.table import Table

from llm_skills_bench.catalog import load_catalog
from llm_skills_bench.schema import Difficulty


@click.group()
def main():
    """LLM Skills Bench — evaluate LLM performance across skill dimensions."""


@main.command()
@click.option("--model", required=True, help="Model identifier (e.g. gpt-4o, claude-3-5-sonnet).")
@click.option("--skills", default="", help="Comma-separated skill names to evaluate.")
@click.option("--results-dir", default="./results", show_default=True, type=click.Path())
@click.option("--judge-model", default=None, help="Model for llm_judge scoring (defaults to --model).")
def run(model, skills, results_dir, judge_model):
    """Run the benchmark against a model."""
    from llm_skills_bench.adapters import get_adapter
    from llm_skills_bench.runner import run_benchmark

    skills_filter = [s.strip() for s in skills.split(",") if s.strip()]
    adapter = get_adapter(model)
    judge_adapter = get_adapter(judge_model) if judge_model else adapter

    catalog = load_catalog()
    task_count = len(
        [t for t in catalog if not skills_filter or t.skill.lower() in [s.lower() for s in skills_filter]]
    )
    rprint(f"[bold]Running[/bold] {task_count} tasks with model [cyan]{model}[/cyan]")

    result = run_benchmark(
        model=model,
        skills_filter=skills_filter,
        adapter=adapter,
        judge_adapter=judge_adapter,
        catalog=catalog,
        results_dir=Path(results_dir),
    )

    table = Table(title="Results Summary")
    table.add_column("Skill", style="magenta")
    table.add_column("Mean Score", style="cyan")
    for skill, mean in sorted(result.summary.items()):
        table.add_row(skill, f"{mean:.2%}")
    rprint(table)
    rprint(f"\nResults saved to [bold]{Path(results_dir) / result.run_id}.json[/bold]")


@main.command()
@click.option("--port", default=8080, show_default=True, help="Port to listen on.")
def serve(port):
    """Start the web dashboard server."""
    click.echo("Not implemented yet")


@main.command(name="list")
@click.option(
    "--skills-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing skill YAML files.",
)
def list_skills(skills_dir: Path | None):
    """List available skills in the catalog."""
    tasks = load_catalog(skills_dir)

    table = Table(title="LLM Skills Catalog")
    table.add_column("Task ID", style="cyan")
    table.add_column("Skill", style="magenta")
    table.add_column("Difficulty")
    table.add_column("Scoring Method", style="dim")

    DIFF_STYLE = {
        Difficulty.easy: "green",
        Difficulty.medium: "yellow",
        Difficulty.hard: "red",
    }
    for task in tasks:
        style = DIFF_STYLE[task.difficulty]
        table.add_row(
            task.task_id,
            task.skill,
            f"[{style}]{task.difficulty.value}[/{style}]",
            task.scoring_method.value,
        )

    rprint(table)
    rprint(
        f"\n[bold]Total:[/bold] {len(tasks)} tasks across "
        f"{len({t.skill for t in tasks})} skills"
    )
