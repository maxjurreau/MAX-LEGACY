"""Knowledge layer for Universe-Max.

Encapsulates knowledge-loading helpers. Uses existing store APIs; no new
storage layers introduced.
"""
from __future__ import annotations

from typing import Optional, Iterable, Dict, Any


def load_knowledge(store, obj_id: str) -> Optional[Dict[str, Any]]:
    try:
        return store.load_knowledge(obj_id)
    except Exception:
        return None


def list_knowledge(store) -> Iterable[str]:
    try:
        return list(store.list_knowledge())
    except Exception:
        return []
