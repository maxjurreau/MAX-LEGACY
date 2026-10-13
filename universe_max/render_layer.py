"""Render layer for Universe-Max.

Simple view rendering utilities that produce JSON-friendly views. These are
intended as lightweight adapters to the existing rendering/runtime views.
"""
from __future__ import annotations

from typing import Any, Dict


def render_view(icv, obj_id: str) -> Dict[str, Any]:
    try:
        know = icv.knowledge(obj_id)
        analysis = icv.analyze(obj_id)
        alignment = icv.alignment(obj_id)
        return {"id": obj_id, "title": know.get("title") if know else None, "analysis": analysis, "alignment": alignment}
    except Exception as e:
        return {"id": obj_id, "error": str(e)}
