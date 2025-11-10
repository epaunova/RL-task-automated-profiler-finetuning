"""File-system utilities for writing experiment logs (reference implementation)."""

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
    base = Path(base_dir)
    output_dir = base / experiment_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return RunArtifacts(
        output_dir=output_dir,
        requests_path=output_dir / "requests.jsonl",
        responses_path=output_dir / "responses.jsonl",
        summary_path=output_dir / "summary.json",
    )


def write_requests(path: Path, records: Iterable[logging_utils.RequestLog]) -> None:
    payloads = [logging_utils.request_to_dict(record) for record in records]
    logging_utils.write_jsonl(path, payloads)


def write_responses(path: Path, records: Iterable[logging_utils.ResponseLog]) -> None:
    payloads = [logging_utils.response_to_dict(record) for record in records]
    logging_utils.write_jsonl(path, payloads)


def write_summary(path: Path, summary: Dict[str, float]) -> None:
    logging_utils.write_summary(path, summary)
