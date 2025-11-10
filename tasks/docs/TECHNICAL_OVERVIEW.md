# Technical Overview: Anthropic Experiment Profiler Task

## Purpose
The repository packages a reinforcement-learning task where an agent builds a command-line tool to profile Anthropic Claude finetuning experiments. The implementation mirrors production workflows: it loads structured experiment manifests, orchestrates mockable API calls, records logs, and computes quality metrics for evaluation.

## Architecture
The codebase is split into the following layers:

| Layer | Key Modules | Responsibilities |
| --- | --- | --- |
| CLI | `reference_submission/experiment_profiler/cli.py` | Exposes `run` and `summarize` subcommands. The CLI wires up configuration parsing, experiment execution, and rich/terminal output. It now ships with a graceful fallback so the tool works even when the optional `rich` package is unavailable. |
| Execution core | `reference_submission/experiment_profiler/runner.py` | Coordinates dataset iteration, API calls, metric computation, and artifact writing. Returns `RunResult` with both the file paths and aggregated metric dictionary. |
| Configuration | `reference_submission/experiment_profiler/config.py` | Validates YAML manifests, resolves dataset paths relative to the repo, and instantiates strongly typed dataclasses consumed by the runner. |
| Simulation & tools | `reference_submission/experiment_profiler/simulation.py`, `tools/anthropic_client.py`, `tools/dataset.py`, `tools/logging_utils.py`, `tools/metrics.py` | Provide realistic infrastructure: a client that prefers the real Anthropic SDK but falls back to deterministic mocks, dataset readers, canonical logging schema helpers, and metric implementations (fact coverage, refusal flag, aggregate statistics). |
| Persistence | `reference_submission/experiment_profiler/storage.py` | Creates run directories under `runs/`, writes JSONL request/response logs, and stores aggregated summaries. |
| Grading | `grader/grade.py` | Imports the starter submission, runs the CLI end to end, and verifies that outputs match the contract defined in `prompt.md`. |

Starter counterparts mirror the reference modules but contain TODOs for the RL agent to complete. The grader imports from the starter package during evaluation.

## Data Flow
1. **Configuration parsing:** The CLI reads a YAML manifest via `ExperimentConfig.from_yaml`, which resolves relative dataset paths and extracts run parameters (model, temperature, max tokens, requested metrics).
2. **Client selection:** `ClientFactory` chooses `AnthropicClient` when the `ANTHROPIC_API_KEY` environment variable and SDK are available; otherwise it supplies a `MockAnthropicClient` backed by `data/mock_responses.json` for deterministic behavior.
3. **Experiment loop:** `ExperimentRunner.run` iterates over dialogue samples from `data/dialogues.json`, logs prompts, requests completions from the selected client, captures responses, and gathers per-dialogue metrics.
4. **Aggregation & storage:** Metrics are aggregated with `metrics.aggregate_metrics`, then `storage.write_*` helpers persist request logs, response logs, and the aggregated `summary.json` under `runs/<experiment_id>/`.
5. **Reporting:** The CLI prints status messages. The `summarize` command loads `summary.json` and renders it as either a Rich table (if available) or an aligned plain-text table.

## Optional Dependencies
- `rich` is now strictly optional. When it is missing, the `_ConsoleWrapper` strips Rich markup tags and prints plain strings, while the fallback summary renderer produces an ASCII table.
- `anthropic` remains optional; absence of the SDK or API key automatically routes through the mock client without failing tests.

## Verification & Testing
- `pytest` executes `tasks/experiment_profiler/grader/tests/test_reference_submission.py`, which runs the grading script against the reference implementation to ensure behavioral coverage.
- Manual smoke tests can be executed via:
  ```bash
  python -m tasks.experiment_profiler.reference_submission.experiment_profiler.cli \
      run \
      --config tasks/experiment_profiler/configs/sample_experiment.yaml \
      --output-dir runs/sample

  python -m tasks.experiment_profiler.reference_submission.experiment_profiler.cli \
      summarize \
      --log-dir runs/sample/demo_run
  ```
  The commands succeed in both Rich-present and Rich-free environments.

## Extensibility Notes
- New metrics can be added by extending `tools/metrics.py` and updating both the runner aggregation logic and grader expectations.
- Additional experiment manifests can be dropped into `configs/` and referenced during RL evaluation without code changes.
- The deterministic mock client enables unit tests to run offline; integration tests with the live API only require exporting `ANTHROPIC_API_KEY`.
