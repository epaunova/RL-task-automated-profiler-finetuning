"""Dataset loader utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class DialogueSample:
    dialogue_id: str
    system: str
    user: str
    required_facts: List[str]


def load_dialogues(path: str | Path) -> Iterable[DialogueSample]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    for item in data:
        yield DialogueSample(
            dialogue_id=item["dialogue_id"],
            system=item["system"],
            user=item["user"],
            required_facts=list(item.get("required_facts", [])),
        )
