"""Identity layer for Universe-Max.

Small helpers to resolve identity information for knowledge objects using the
existing store/runtime interfaces.
"""
from __future__ import annotations

from typing import Optional, Dict, Any


def resolve_identity(store, obj_id: str) -> Optional[Dict[str, Any]]:
    try:
        obj = store.load_knowledge(obj_id)
    except Exception:
        return None
    if not obj:
        return None
    return {"id": obj.get("id"), "entity_id": obj.get("entity_id"), "author": obj.get("author")}
