from __future__ import annotations

from typing import List, Optional
from runtime.store import MAXLegacyStore


class IdentityLayer:
    """Resolve and index identities across knowledge objects.

    This layer does not create new identities; it maps existing stored objects
    that include identity-like fields (e.g., 'entity_id', 'author').
    """

    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)

    def find_by_entity(self, entity_id: str) -> List[dict]:
        out = []
        for p in self.store.knowledge_dir.glob("*.json"):
            try:
                data = p.read_text(encoding="utf-8")
                obj = __import__("json").loads(data)
                if obj.get("entity_id") == entity_id or obj.get("id") == entity_id:
                    out.append(obj)
            except Exception:
                continue
        return out

    def count_identities(self) -> int:
        # crude count of unique entity_id fields
        s = set()
        for p in self.store.knowledge_dir.glob("*.json"):
            try:
                obj = __import__("json").loads(p.read_text(encoding="utf-8"))
                if obj.get("entity_id"):
                    s.add(obj.get("entity_id"))
            except Exception:
                continue
        return len(s)
