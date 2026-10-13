"""Reality evaluation layer for Universe-Max.

Uses ICV alignment and the store to produce a reality-evaluation result.
"""
from __future__ import annotations

from typing import Any, Dict


def evaluate_reality(icv, obj_id: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        a = icv.alignment(obj_id)
        out["alignment"] = a
        # also include analysis fallback
        out["analysis"] = icv.analyze(obj_id)
    except Exception as e:
        out["error"] = str(e)
    return out
