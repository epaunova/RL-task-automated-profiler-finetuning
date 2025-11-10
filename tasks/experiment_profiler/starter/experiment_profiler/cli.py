"""CLI definition for the experiment profiler (starter version)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .config import ExperimentConfig
from .runner import ExperimentRunner
from .simulation import ClientFactory

CONSOLE = Console()


@click.group()
def cli() -> None:
    """Entry point for the experiment profiler CLI."""


@cli.command()
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path), required=True)
def run(config_path: Path, output_dir: Path) -> None:
    """Execute a profiling run and write logs to the output directory."""

    # TODO: Load the configuration, run the experiment, and report success.
    raise NotImplementedError


@cli.command()
@click.option("--log-dir", type=click.Path(file_okay=False, exists=True, path_type=Path), required=True)
def summarize(log_dir: Path) -> None:
    """Pretty-print metrics from a previous run."""

    # TODO: Load the configuration summary and print it via `rich`.
    raise NotImplementedError


if __name__ == "__main__":
    cli()
