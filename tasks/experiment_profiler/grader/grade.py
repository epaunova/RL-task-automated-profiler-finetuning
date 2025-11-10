"""Deterministic grader for the experiment profiler task."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.experiment_profiler.tools import dataset, metrics

CONFIG_PATH = ROOT / "configs" / "sample_experiment.yaml"
RESPONSES_PATH = ROOT / "data" / "mock_responses.json"
DATASET_PATH = ROOT / "data" / "dialogues.json"


class GradingError(Exception):
    """Raised when the submission violates a grading constraint."""


def _load_submission(package_root: Path) -> None:
    sys.path.insert(0, str(package_root))
    for module in list(sys.modules):
        if module.startswith("experiment_profiler"):
            del sys.modules[module]


def _grade_submission(package_root: Path) -> Dict[str, Any]:
    _load_submission(package_root)

    config_module = importlib.import_module("experiment_profiler.config")
    runner_module = importlib.import_module("experiment_profiler.runner")
    simulation_module = importlib.import_module("experiment_profiler.simulation")

    ExperimentConfig = getattr(config_module, "ExperimentConfig")
    ExperimentRunner = getattr(runner_module, "ExperimentRunner")
    ClientFactory = getattr(simulation_module, "ClientFactory")

    config = ExperimentConfig.from_yaml(CONFIG_PATH)
    factory = ClientFactory(RESPONSES_PATH)
    runner = ExperimentRunner(config=config, factory=factory)

    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.run(tmpdir)
        summary = runner.summarize(result.artifacts.output_dir)
        _validate_artifacts(result.artifacts.output_dir, summary)

    return {"status": "pass", "details": summary}


def _validate_artifacts(log_dir: Path, summary: Dict[str, Any]) -> None:
    requests_path = log_dir / "requests.jsonl"
    responses_path = log_dir / "responses.jsonl"
    summary_path = log_dir / "summary.json"

    if not requests_path.exists():
        raise GradingError("requests.jsonl not found")
    if not responses_path.exists():
        raise GradingError("responses.jsonl not found")
    if not summary_path.exists():
        raise GradingError("summary.json not found")

    with requests_path.open("r", encoding="utf-8") as handle:
        requests = [json.loads(line) for line in handle if line.strip()]
    with responses_path.open("r", encoding="utf-8") as handle:
        responses = [json.loads(line) for line in handle if line.strip()]

    if len(requests) != len(responses):
        raise GradingError("Mismatched number of requests and responses")
    if len(requests) != 3:
        raise GradingError("Expected exactly 3 prompts in the dataset")

    dataset_samples = list(dataset.load_dialogues(DATASET_PATH))

    for request, sample in zip(requests, dataset_samples):
        if request.get("dialogue_id") != sample.dialogue_id:
            raise GradingError("Dialogue IDs in requests do not match dataset order")
        prompt = request.get("prompt", {})
        if prompt.get("system") != sample.system or prompt.get("user") != sample.user:
            raise GradingError("Prompt content mismatch in request log")
        if request.get("model") is None or request.get("temperature") is None:
            raise GradingError("Request missing model metadata")

    for response, sample in zip(responses, dataset_samples):
        if response.get("dialogue_id") != sample.dialogue_id:
            raise GradingError("Dialogue IDs in responses do not match dataset order")
        completion = response.get("completion", "")
        metadata = {k: v for k, v in response.items() if k not in {"dialogue_id", "completion"}}
        coverage = metrics.compute_fact_coverage(sample.required_facts, completion)
        refusal = metrics.compute_refusal_flag(completion, metadata)
        if coverage < 0.6 and sample.dialogue_id != "alignment_eval":
            raise GradingError("Completion missing required facts")
        if sample.dialogue_id == "alignment_eval" and not refusal:
            raise GradingError("Expected refusal for alignment_eval prompt")

    expected_summary = metrics.aggregate_metrics(
        [metrics.compute_fact_coverage(s.required_facts, r.get("completion", "")) for s, r in zip(dataset_samples, responses)],
        [metrics.compute_refusal_flag(r.get("completion", ""), {k: v for k, v in r.items() if k not in {"dialogue_id", "completion"}}) for r in responses],
    )

    for key, expected in expected_summary.items():
        actual = summary.get(key)
        if actual is None:
            raise GradingError(f"Summary missing metric {key}")
        if abs(float(actual) - float(expected)) > 1e-3:
            raise GradingError(f"Metric {key} mismatch: expected {expected}, got {actual}")


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Grade the experiment profiler task")
    parser.add_argument("--use-reference", action="store_true", help="Validate the reference solution instead of the starter")
    args = parser.parse_args(argv)

    package_dir = ROOT / ("reference_submission" if args.use_reference else "starter")
    try:
        result = _grade_submission(package_dir)
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "fail", "error": str(exc)}))
        raise SystemExit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
