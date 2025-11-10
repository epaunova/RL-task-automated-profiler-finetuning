# Experiment Profiler RL Task

This directory implements the recommended RL task where the model builds a CLI
that profiles Anthropic Claude finetuning experiments.  It is the same task
outlined in the design discussion—complete with tooling, datasets, configs, and
a deterministic grader.

## Contents

- `prompt.md` — the exact instructions shown to the model.
- `starter/` — the repository state that the model sees at the beginning of the
  episode.
- `tools/` — helper modules that emulate realistic infrastructure (API, dataset
  loader, logging helpers, metric calculators).
- `configs/` and `data/` — lightweight artifacts the model must consume.
- `grader/` — the deterministic evaluation harness.
- `reference_submission/` — a correct implementation used in tests and as a
  blueprint for reviewers.

## Task summary

The model has to:

1. Build a CLI (`experiment-profiler`) that can run a batch of conversations
   defined in a YAML experiment config.
2. Use the Anthropic client (real or simulated) to obtain completions.
3. Log each prompt/response pair using the canonical JSONL schema in
   `tools.logging_utils`.
4. Compute fact coverage and refusal rate metrics.
5. Produce a summary report with aggregated metrics.

The grader executes the CLI with the sample configuration and validates all of
these behaviors.

## Tooling and API usage

`tools/anthropic_client.py` exposes a single entry point that always works:

- When `ANTHROPIC_API_KEY` is exported, the helper issues real Claude requests.
- Without a key, the helper falls back to the deterministic mock responses in
  `data/mock_responses.json` so grading stays stable.

Either mode satisfies the task requirements, and the grader accepts both.

## Viewing the metrics as tables

1. **Run the experiment** (reference implementation shown for clarity):

   ```bash
   python -m tasks.experiment_profiler.reference_submission.experiment_profiler.cli \
       run \
       --config tasks/experiment_profiler/configs/sample_experiment.yaml \
       --output-dir runs/sample
   ```

   After this command, the aggregated metrics live in
   `runs/sample/summary.json`.

2. **Print a Rich table in the terminal**:

   ```bash
   python -m tasks.experiment_profiler.reference_submission.experiment_profiler.cli \
       summarize \
       --log-dir runs/sample
   ```

   The `summarize` subcommand renders a formatted table (using Rich) so you can
   copy or screenshot it directly.

3. **Generate Markdown if needed**:

   ```bash
   python - <<'PY'
   import json
   from pathlib import Path

   summary = json.loads(Path('runs/sample/summary.json').read_text())
   print('| Metric | Value |')
   print('| --- | ---: |')
   for key, value in summary.items():
       if isinstance(value, (int, float)):
           print(f"| {key} | {value:.4f} |")
       else:
           print(f"| {key} | {value} |")
   PY
   ```
