# RL Task: Anthropic Experiment Profiler

This repository implements the exact RL task that was described in the earlier
recommendation: building an automated profiler for Anthropic Claude finetuning
experiments.  Nothing from the old “AI Physicist” project remains—the repo is a
self-contained starter kit focused solely on the experiment-profiler workflow.

## What the task teaches

The assignment mirrors the day-to-day responsibilities of an ML engineer.  The
model must:
parse YAML experiment manifests and select runs to execute;
- orchestrate a tooling stack that includes a (mockable) Anthropic API client,
  dataset loader, logging helpers, and metric calculators;
- expose a CLI for running experiments and summarizing the collected results;
- persist detailed logs and quality metrics for every prompt/response pair.

The grading harness checks each of these behaviors, producing a realistic but
verifiable engineering challenge for RL fine-tuning.

## Repository layout
```
.
├── README.md
├── pyproject.toml
├── requirements.txt
└── tasks
    └── experiment_profiler
        ├── README.md
        ├── prompt.md
        ├── configs
        │   └── sample_experiment.yaml
        ├── data
        │   ├── dialogues.json
        │   └── mock_responses.json
        ├── grader
        │   ├── __init__.py
        │   ├── grade.py
        │   └── tests
        │       └── test_reference_submission.py
        ├── reference_submission
        │   └── experiment_profiler
        │       ├── __init__.py
        │       ├── cli.py
        │       ├── config.py
        │       ├── runner.py
        │       ├── simulation.py
        │       └── storage.py
        ├── starter
        │   └── experiment_profiler
        │       ├── __init__.py
        │       ├── cli.py
        │       ├── config.py
        │       ├── runner.py
        │       ├── simulation.py
        │       └── storage.py
        └── tools
            ├── __init__.py
            ├── anthropic_client.py
            ├── dataset.py
            ├── logging_utils.py
            └── metrics.py
```

The starter package mirrors the reference solution but deliberately leaves
TODOs that the model must fill in.  The grader imports the implementation from
the starter package when evaluating a submission.

## Tooling and API keys
The task **does include a tool**: `tasks/experiment_profiler/tools/anthropic_client.py`.
This helper module exposes the same interface whether or not a real Anthropic
API key is available:
If the `ANTHROPIC_API_KEY` environment variable is set, the tool forwards
  requests to the live Claude API.
- Otherwise, it deterministically simulates responses using
  `data/mock_responses.json`, ensuring that grading is reproducible without
  external dependencies.

  Additional utilities—`dataset.py`, `logging_utils.py`, and `metrics.py`—complete
the toolchain that the model wires together

## Quick start
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the grader against the reference submission** (for smoke testing)
   ```bash
   python -m tasks.experiment_profiler.grader.grade --use-reference
   ```
3. **Reset to the starter state** before launching an RL episode.  The `starter`
   package is what the model sees at the beginning of the task.  The RL loop
   should provide the model with write access to the repository and run the
   grader to determine success.

## Testing philosophy
The grading script focuses on behavior rather than exact code.  It checks that:
Experiments are executed according to the YAML configuration.
- All prompts are logged to disk with the expected schema.
- Metrics such as fact coverage and completion rate are computed and persisted.
- The CLI exposes commands for both running and summarizing experiments.
- The prompt supplied to the model mirrors these checks to make the task well
specified.

## Additional documentation
- `docs/TECHNICAL_OVERVIEW.md` — architecture, data flow, and extensibility
  notes for reviewers.
- `docs/SAMPLE_RESULTS.md` — captured metrics from running the reference CLI
  with the fallback ASCII renderer.

## Presenting results
When you run the reference CLI (or a learner submission) it writes JSON logs
under `runs/<experiment_id>/`.  The key artifact is
`runs/<experiment_id>/summary.json`, which already aggregates the quality
metrics needed by the grader.

### 1. Produce the metrics
```bash
python -m tasks.experiment_profiler.reference_submission.experiment_profiler.cli \
    run \
    --config tasks/experiment_profiler/configs/sample_experiment.yaml \
    --output-dir runs/sample
```
This creates `runs/sample/summary.json` together with per-dialogue logs.

### 2. Render an on-screen table
The `summarize` command uses the bundled Rich dependency to print a table like
the following directly in your terminal when `rich` is installed.  If the
package is missing (for example, in an offline evaluation environment) the CLI
falls back to a neatly aligned ASCII table with the exact same metrics.

```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Experiment Metrics (sample) ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Metric           │ Value  │
├──────────────────┼────────┤
│ fact_coverage    │ 0.8333 │
│ refusal_rate     │ 0.0000 │
│ geometric_mean   │ 0.9129 │
└──────────────────┴────────┘
```
