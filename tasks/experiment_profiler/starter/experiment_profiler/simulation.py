"""Simulation utilities (starter version)."""

from __future__ import annotations

from pathlib import Path

from tasks.experiment_profiler.tools.anthropic_client import MockAnthropicClient


class ClientFactory:
    """Factory responsible for creating Anthropic clients."""

    def __init__(self, responses_path: str | Path) -> None:
        self.responses_path = Path(responses_path)

    def build_simulator(self) -> MockAnthropicClient:
        return MockAnthropicClient(str(self.responses_path))

    def build_live_or_simulated(self, model: str, max_tokens: int, temperature: float):
        """Return a live Anthropic client if possible, otherwise fall back to the simulator."""

        # TODO: Instantiate `AnthropicClient` with the simulator fallback.
        raise NotImplementedError
