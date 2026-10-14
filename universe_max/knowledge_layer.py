"""Knowledge layer that wraps MAXLegacyStore for Universe-MAX.

Provides small helpers for saving, loading and querying knowledge objects.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from runtime.store import MAXLegacyStore


class KnowledgeManager:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store

    def save(self, obj: Dict[str, Any]) -> str:
        return self.store.save_knowledge(obj)

    def load(self, obj_id: str) -> Dict[str, Any]:
        return self.store.load_knowledge(obj_id)

    def list_ids(self) -> List[str]:
        return self.store.list_knowledge()

    def find_by_type(self, t: str) -> List[Dict[str, Any]]:
        res = []
        for _id in self.list_ids():
            obj = self.load(_id)
            if obj.get("type") == t:
                res.append(obj)
        return res

    def exists(self, obj_id: str) -> bool:
        try:
            self.load(obj_id)
            return True
        except Exception:
            return False
