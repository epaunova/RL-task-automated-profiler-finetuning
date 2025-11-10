"""Experiment configuration models (reference implementation)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from tasks.experiment_profiler.tools.config_loader import load_yaml

REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass
class ExperimentConfig:
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
        config_path = Path(path).expanduser().resolve()
        payload = load_yaml(config_path)

        dataset_path = Path(payload["dataset_path"]).expanduser()
        if not dataset_path.is_absolute():
            candidate = (config_path.parent / dataset_path).resolve()
            if candidate.exists():
                dataset_path = candidate
            else:
                dataset_path = (REPO_ROOT / dataset_path).resolve()

        return cls(
            experiment_id=str(payload["experiment_id"]),
            model=str(payload["model"]),
            max_tokens=int(payload["max_tokens"]),
            temperature=float(payload["temperature"]),
            dataset_path=dataset_path,
            log_schema_version=int(payload.get("log_schema_version", 1)),
            output_fields=list(payload.get("output_fields", [])),
            metrics=list(payload.get("metrics", [])),
        )
