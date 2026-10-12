from __future__ import annotations

from typing import Dict, List, Any
from runtime.store import MAXLegacyStore


class KnowledgeViews:
    """Generic knowledge object views and render-friendly summaries."""

    def __init__(self, root=None):
        self.store = MAXLegacyStore(root=root)

    def get_summary(self, obj_id: str) -> Dict[str, Any]:
        obj = self.store.load_knowledge(obj_id)
        # produce a minimal, safe summary
        return {
            "id": obj.get("id"),
            "title": obj.get("title") or obj.get("name"),
            "type": obj.get("type"),
            "district": obj.get("district"),
            "icv": obj.get("icv"),
            "domain": obj.get("domain"),
        }

    def search_by_title(self, term: str) -> List[Dict[str, Any]]:
        term_low = term.lower()
        results: List[Dict[str, Any]] = []
        for p in self.store.knowledge_dir.glob("*.json"):
            try:
                obj = p.read_text(encoding="utf-8")
                data = json.loads(obj)
                title = (data.get("title") or data.get("name") or "").lower()
                if term_low in title:
                    results.append({"id": data.get("id"), "title": data.get("title") or data.get("name")})
            except Exception:
                continue
        return results


