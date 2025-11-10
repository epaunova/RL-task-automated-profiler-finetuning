"""Thin wrapper around the Anthropic SDK with a deterministic fallback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict

try:  # pragma: no cover - import guarded for optional dependency
    import anthropic
except Exception:  # pragma: no cover
    anthropic = None  # type: ignore

from .dataset import DialogueSample


@dataclass
class AnthropicResponse:
    """Minimal response payload used by the grader."""

    completion: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        payload = {"completion": self.completion}
        payload.update(self.metadata)
        return payload


class AnthropicClient:
    """Client that proxies to the real Anthropic API when possible."""

    def __init__(self, model: str, max_tokens: int, temperature: float, *, simulator: "MockAnthropicClient") -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.simulator = simulator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        self._client = None
        if api_key and anthropic is not None:
            self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, sample: DialogueSample) -> AnthropicResponse:
        if self._client is None:
            return self.simulator.complete(sample, self.model, self.temperature)

        message = self._client.messages.create(  # pragma: no cover - requires network
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=sample.system,
            messages=[{"role": "user", "content": sample.user}],
        )
        completion = message.content[0].text  # type: ignore[assignment]
        metadata = {
            "model": self.model,
            "temperature": self.temperature,
            "token_count": getattr(message, "usage", {}).get("output_tokens", 0),
        }
        return AnthropicResponse(completion=completion, metadata=metadata)


class MockAnthropicClient:
    """Deterministic simulator backed by `mock_responses.json`."""

    def __init__(self, response_path: str) -> None:
        with open(response_path, "r", encoding="utf-8") as handle:
            self._responses = json.load(handle)

    def complete(self, sample: DialogueSample, model: str, temperature: float) -> AnthropicResponse:
        payload = self._responses.get(sample.dialogue_id)
        if not payload:
            raise KeyError(f"No mock response for dialogue_id={sample.dialogue_id}")

        metadata = dict(payload.get("metadata", {}))
        metadata.setdefault("model", model)
        metadata.setdefault("temperature", temperature)
        return AnthropicResponse(completion=payload["completion"], metadata=metadata)
