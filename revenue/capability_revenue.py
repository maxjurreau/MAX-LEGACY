"""Capability revenue mapping utilities."""
from __future__ import annotations

from typing import Any, Dict


def calculate_capability_value(capability: Dict[str, Any]) -> float:
    # simple heuristic: base price * scale
    base = float(capability.get("base_price", 0.0))
    scale = float(capability.get("scale", 1.0))
    return base * scale
