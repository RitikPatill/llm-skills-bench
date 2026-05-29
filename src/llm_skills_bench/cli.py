import click


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
def list_skills():
    """List available skills in the catalog."""
    click.echo("Not implemented yet")
