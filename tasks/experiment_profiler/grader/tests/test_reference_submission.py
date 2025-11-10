from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
GRADER = ROOT / "tasks" / "experiment_profiler" / "grader" / "grade.py"


def test_reference_submission_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(GRADER), "--use-reference"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert "fact_coverage" in payload["details"]
