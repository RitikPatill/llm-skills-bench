from llm_skills_bench import __version__


def test_version():
    assert __version__ == "0.1.0"


def test_cli_help(capsys):
    from click.testing import CliRunner
    from llm_skills_bench.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "serve" in result.output
    assert "list" in result.output
