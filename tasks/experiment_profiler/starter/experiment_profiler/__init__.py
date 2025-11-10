"""Starter package for the experiment profiler task."""

__all__ = ["cli"]


def __getattr__(name):  # pragma: no cover - simple accessor
    if name == "cli":
        from .cli import cli

        return cli
    raise AttributeError(name)
