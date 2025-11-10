"""CLI definition for the experiment profiler (reference implementation)."""

from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .config import ExperimentConfig
from .runner import ExperimentRunner
from .simulation import ClientFactory

CONSOLE = Console()
DEFAULT_RESPONSES = Path(__file__).resolve().parents[2] / "data" / "mock_responses.json"


def _build_runner(config_path: Path) -> ExperimentRunner:
    config = ExperimentConfig.from_yaml(config_path)
    factory = ClientFactory(DEFAULT_RESPONSES)
    return ExperimentRunner(config=config, factory=factory)


@click.group()
def cli() -> None:
    """Entry point for the experiment profiler CLI."""


@cli.command()
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path), required=True)
def run(config_path: Path, output_dir: Path) -> None:
    """Execute a profiling run and write logs to the output directory."""

    runner = _build_runner(config_path)
    result = runner.run(output_dir)
    CONSOLE.print(f"[green]Completed experiment {runner.config.experiment_id}[/green]")
    CONSOLE.print(f"Metrics written to [bold]{result.artifacts.summary_path}[/bold]")


@cli.command()
@click.option("--log-dir", type=click.Path(file_okay=False, exists=True, path_type=Path), required=True)
def summarize(log_dir: Path) -> None:
    """Pretty-print metrics from a previous run."""

    summary_path = log_dir / "summary.json"
    if not summary_path.exists():
        raise click.ClickException(f"Summary file not found at {summary_path}")

    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)

    table = Table(title=f"Experiment Metrics ({summary_path.parent.name})")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            table.add_row(key, f"{value:.4f}")
        else:
            table.add_row(key, str(value))
    CONSOLE.print(table)


if __name__ == "__main__":
    cli()
