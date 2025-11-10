"""Core execution logic for the experiment profiler (starter version)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from tasks.experiment_profiler.tools import dataset, logging_utils, metrics

from .config import ExperimentConfig
from .simulation import ClientFactory
from .storage import RunArtifacts, prepare_output_dir, write_requests, write_responses, write_summary


@dataclass
class RunResult:
    artifacts: RunArtifacts
    metrics: dict


class ExperimentRunner:
    def __init__(self, config: ExperimentConfig, factory: ClientFactory) -> None:
        self.config = config
        self.factory = factory

    def run(self, output_dir: str | None = None) -> RunResult:
        """Execute the configured experiment."""

        # TODO: Load dataset, iterate prompts, collect logs, compute metrics, and persist outputs.
        raise NotImplementedError

    def summarize(self, log_dir: str) -> dict:
        """Load an existing summary.json file and return its contents."""

        # TODO: Implement log loading/validation logic.
        raise NotImplementedError
