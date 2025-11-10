"""Core execution logic for the experiment profiler (reference implementation)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from tasks.experiment_profiler.tools import dataset, logging_utils, metrics

from .config import ExperimentConfig
from .simulation import ClientFactory
from .storage import RunArtifacts, prepare_output_dir, write_requests, write_responses, write_summary


@dataclass
class RunResult:
    artifacts: RunArtifacts
    metrics: Dict[str, float]


class ExperimentRunner:
    def __init__(self, config: ExperimentConfig, factory: ClientFactory) -> None:
        self.config = config
        self.factory = factory

    def run(self, output_dir: str | Path | None = None) -> RunResult:
        base_dir = Path(output_dir or "runs")
        artifacts = prepare_output_dir(base_dir, self.config.experiment_id)

        client = self.factory.build_live_or_simulated(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        request_logs: List[logging_utils.RequestLog] = []
        response_logs: List[logging_utils.ResponseLog] = []
        fact_coverages: List[float] = []
        refusals: List[bool] = []

        for sample in dataset.load_dialogues(self.config.dataset_path):
            request_logs.append(
                logging_utils.RequestLog(
                    dialogue_id=sample.dialogue_id,
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    prompt={"system": sample.system, "user": sample.user},
                )
            )
            response = client.complete(sample)
            response_logs.append(
                logging_utils.ResponseLog(
                    dialogue_id=sample.dialogue_id,
                    completion=response.completion,
                    metadata=response.metadata,
                )
            )
            fact_coverages.append(metrics.compute_fact_coverage(sample.required_facts, response.completion))
            refusals.append(metrics.compute_refusal_flag(response.completion, response.metadata))

        summary = metrics.aggregate_metrics(fact_coverages, refusals)

        write_requests(artifacts.requests_path, request_logs)
        write_responses(artifacts.responses_path, response_logs)
        write_summary(artifacts.summary_path, summary)

        return RunResult(artifacts=artifacts, metrics=summary)

    def summarize(self, log_dir: str | Path) -> Dict[str, float]:
        summary_path = Path(log_dir) / "summary.json"
        if not summary_path.exists():
            raise FileNotFoundError(f"Summary file not found at {summary_path}")
        with summary_path.open("r", encoding="utf-8") as handle:
            summary: Dict[str, float] = json.load(handle)
        return summary
