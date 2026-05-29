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
def run(model, skills):
    """Run the benchmark against a model."""
    click.echo("Not implemented yet")


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
