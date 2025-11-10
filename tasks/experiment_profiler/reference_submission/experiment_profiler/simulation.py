"""Simulation utilities (reference implementation)."""

from __future__ import annotations

from pathlib import Path

from tasks.experiment_profiler.tools.anthropic_client import AnthropicClient, MockAnthropicClient


class ClientFactory:
    def __init__(self, responses_path: str | Path) -> None:
        self.responses_path = Path(responses_path)

    def build_simulator(self) -> MockAnthropicClient:
        return MockAnthropicClient(str(self.responses_path))

    def build_live_or_simulated(self, model: str, max_tokens: int, temperature: float) -> AnthropicClient:
        simulator = self.build_simulator()
        return AnthropicClient(model=model, max_tokens=max_tokens, temperature=temperature, simulator=simulator)
