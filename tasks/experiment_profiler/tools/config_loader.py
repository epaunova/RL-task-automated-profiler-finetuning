"""Minimal YAML loader with graceful fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


def _coerce(value: str) -> Any:
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_minimal_yaml(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current_key is None:
                raise ValueError("List item encountered before key definition")
            data.setdefault(current_key, []).append(_coerce(line[2:].strip()))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = _coerce(value)
                current_key = None
            else:
                data[key] = []
                current_key = key
        else:
            raise ValueError(f"Unsupported line: {raw_line}")
    return data


def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        payload = yaml.safe_load(text)
        if not isinstance(payload, dict):
            raise TypeError("Top-level YAML structure must be a mapping")
        return payload
    return _parse_minimal_yaml(text)
