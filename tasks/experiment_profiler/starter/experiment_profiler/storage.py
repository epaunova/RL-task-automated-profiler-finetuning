"""File-system utilities for writing experiment logs (starter version)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from tasks.experiment_profiler.tools import logging_utils


@dataclass
class RunArtifacts:
    output_dir: Path
    requests_path: Path
    responses_path: Path
    summary_path: Path


def prepare_output_dir(base_dir: str | Path, experiment_id: str) -> RunArtifacts:
    """Create the output directory tree for a run."""

    # TODO: Implement deterministic directory creation (e.g., `<base>/<experiment_id>`).
    raise NotImplementedError


def write_requests(path: Path, records: Iterable[logging_utils.RequestLog]) -> None:
    """Persist request payloads as JSONL."""

    # TODO: Convert dataclass instances to dictionaries and delegate to logging_utils.
    raise NotImplementedError


def write_responses(path: Path, records: Iterable[logging_utils.ResponseLog]) -> None:
    """Persist response payloads as JSONL."""

    # TODO: Similar to `write_requests` but for responses.
    raise NotImplementedError


def write_summary(path: Path, summary: Dict[str, float]) -> None:
    """Write the aggregated summary JSON file."""

    # TODO: Delegate to `logging_utils.write_summary`.
    raise NotImplementedError
