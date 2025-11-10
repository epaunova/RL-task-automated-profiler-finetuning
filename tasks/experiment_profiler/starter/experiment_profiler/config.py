"""Experiment configuration models (starter version)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from tasks.experiment_profiler.tools.config_loader import load_yaml


@dataclass
class ExperimentConfig:
    """Runtime configuration for a profiling run."""

    experiment_id: str
    model: str
    max_tokens: int
    temperature: float
    dataset_path: Path
    log_schema_version: int
    output_fields: List[str]
    metrics: List[str]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ExperimentConfig":
        """Load and validate an experiment configuration."""

        # TODO: Use `load_yaml` to parse the file, normalize paths, and validate fields.
        raise NotImplementedError
