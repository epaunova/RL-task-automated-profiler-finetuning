"""CLI definition for the experiment profiler (reference implementation)."""

from __future__ import annotations

import json
from pathlib import Path

import click

try:  # pragma: no cover - optional dependency in the execution environment
    from rich.console import Console  # type: ignore
    from rich.table import Table  # type: ignore
except Exception:  # pragma: no cover - falls back to stdlib rendering
    Console = None  # type: ignore
    Table = None  # type: ignore

_MARKUP_RE = __import__("re").compile(r"\[(?:/?)[^\[\]]+\]")

from .config import ExperimentConfig
from .runner import ExperimentRunner
from .simulation import ClientFactory

class _ConsoleWrapper:
    """Minimal console facade that degrades gracefully without Rich."""

    def __init__(self) -> None:
        self._rich_console = Console() if Console is not None else None

    def print(self, message: object) -> None:
        if self._rich_console is not None:
            self._rich_console.print(message)
        else:
            if isinstance(message, str):
                print(_MARKUP_RE.sub("", message))
            else:
                print(message)


CONSOLE = _ConsoleWrapper()
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

    if Table is not None and isinstance(CONSOLE, _ConsoleWrapper) and CONSOLE._rich_console is not None:
        table = Table(title=f"Experiment Metrics ({summary_path.parent.name})")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        for key, value in summary.items():
            if isinstance(value, (int, float)):
                table.add_row(key, f"{value:.4f}")
            else:
                table.add_row(key, str(value))
        CONSOLE.print(table)
        return

    # Fallback: render a simple aligned table using only stdlib features.
    header = f"Experiment Metrics ({summary_path.parent.name})"
    CONSOLE.print(header)
    max_key = max(len("Metric"), *(len(key) for key in summary))
    CONSOLE.print("-" * (max_key + 15))
    CONSOLE.print(f"{'Metric'.ljust(max_key)} | Value")
    CONSOLE.print("-" * (max_key + 15))
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            formatted = f"{value:.4f}"
        else:
            formatted = str(value)
        CONSOLE.print(f"{key.ljust(max_key)} | {formatted}")


if __name__ == "__main__":
    cli()
