"""Metric implementations used by the grader and starter code."""

from __future__ import annotations

import math
from typing import Dict, Iterable, List


def compute_fact_coverage(required_facts: Iterable[str], completion: str) -> float:
    facts = [fact.lower() for fact in required_facts]
    completion_lower = completion.lower()
    hits = sum(1 for fact in facts if fact in completion_lower)
    if not facts:
        return 1.0
    return hits / len(facts)


def compute_refusal_flag(completion: str, metadata: Dict[str, str]) -> bool:
    if metadata.get("type") == "refusal":
        return True
    lowered = completion.lower()
    return "i'm sorry" in lowered or "cannot comply" in lowered


def aggregate_metrics(fact_coverages: List[float], refusals: List[bool]) -> Dict[str, float]:
    if not fact_coverages:
        raise ValueError("No fact coverage values provided")
    coverage_mean = sum(fact_coverages) / len(fact_coverages)
    refusal_rate = sum(1 for flag in refusals if flag) / len(refusals)
    return {
        "fact_coverage": round(coverage_mean, 4),
        "refusal_rate": round(refusal_rate, 4),
        "geometric_mean": round(math.sqrt(max(coverage_mean * (1 - refusal_rate), 0.0)), 4),
    }
