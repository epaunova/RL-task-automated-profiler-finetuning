"""Structured logging helpers used by the grader."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable


@dataclass
class RequestLog:
    dialogue_id: str
    model: str
    temperature: float
    max_tokens: int
    prompt: Dict[str, Any]


@dataclass
class ResponseLog:
    dialogue_id: str
    completion: str
    metadata: Dict[str, Any]


def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_summary(path: Path, summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)


def request_to_dict(request: RequestLog) -> Dict[str, Any]:
    return asdict(request)


def response_to_dict(response: ResponseLog) -> Dict[str, Any]:
    payload = {
        "dialogue_id": response.dialogue_id,
        "completion": response.completion,
    }
    payload.update(response.metadata)
    return payload
