You are an ML engineer working on an evaluation harness for Anthropic Claude fine-tuning
experiments.  The research team wants a command-line tool named `experiment-profiler` that can:

1. Load an experiment configuration from YAML (see `tasks/experiment_profiler/configs`).
2. Iterate over a small dataset of dialogue prompts (`tasks/experiment_profiler/data/dialogues.json`).
3. Query Claude for each prompt using the parameters from the configuration.  When an
   `ANTHROPIC_API_KEY` environment variable is unavailable, you **must** fall back to the deterministic
   simulator provided in `experiment_profiler.simulation.MockAnthropicClient`.
4. Log each prompt/response pair as JSON Lines using the schema documented in
   `tools/logging_utils.py`.  The CLI must create one directory per run containing:
   - `requests.jsonl` — each line holds the request payload sent to Claude.
   - `responses.jsonl` — each line holds the response payload (real or simulated).
   - `summary.json` — aggregated metrics (see below).
5. Compute metrics using `tools.metrics`:
   - `fact_coverage`: fraction of required facts covered in the model response.
   - `refusal_rate`: proportion of prompts for which the model refused to answer
     (responses containing "I’m sorry" or `"type": "refusal"`).
6. Expose two CLI commands via `click`:
   - `run`: executes the experiment and writes logs/metrics into a directory passed via `--output-dir`.
   - `summarize`: reads a log directory and pretty-prints the aggregated metrics using `rich`.

You are given partially implemented modules in `tasks/experiment_profiler/starter/experiment_profiler/`.
Fill in the TODO blocks so that the CLI satisfies all requirements.  The grader will invoke the CLI
as follows:

```bash
python -m experiment_profiler.cli run \
  --config tasks/experiment_profiler/configs/sample_experiment.yaml \
  --output-dir /tmp/experiment-output

python -m experiment_profiler.cli summarize --log-dir /tmp/experiment-output
```

All file paths in the configuration are relative to the repository root.  Do not modify files outside
of the starter package unless absolutely necessary.  Every requirement listed above is validated by
the grader; implementations that skip logging, ignore configuration values, or compute metrics
incorrectly will fail.
