"""Rendering helpers for Universe-MAX runtime views."""
from __future__ import annotations

from typing import Any, Dict, Optional


def render_view(context: Dict[str, Any], simulation_result: Optional[Dict[str, Any]] = None, evaluation: Optional[Dict[str, Any]] = None) -> str:
    parts = []
    parts.append("Universe-MAX Runtime View")
    parts.append(f"Districts: {len(context.get('districts', {}))}")
    parts.append(f"ICVs: {len(context.get('icvs', {}))}")
    if simulation_result is not None:
        summary = simulation_result.get("summary", {})
        parts.append(f"Last simulation: steps={summary.get('steps')} icv_count={summary.get('icv_count')}")
    if evaluation is not None:
        parts.append(f"Evaluation: known_knowledge={len(evaluation.get('known_knowledge_ids', []))} unknown_icvs={len(evaluation.get('unknown_icvs', []))}")
    return "\n".join(parts)
