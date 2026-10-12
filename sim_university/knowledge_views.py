from __future__ import annotations

from typing import Dict, List, Any, Optional
from runtime.store import MAXLegacyStore
from runtime.config import DEFAULT_CONFIG
from runtime.audit import DEFAULT_AUDIT_TRAIL
from runtime.exceptions import MAXLegacyError
import json


class KnowledgeViews:
    """Generic knowledge object views and render-friendly summaries.

    This module provides safe read helpers for UI and API layers. It does not
    mutate stored objects.
    """

    def __init__(self, root: Optional[str] = None):
        repo_root = root
        self.store = MAXLegacyStore(root=repo_root) if repo_root is not None else MAXLegacyStore()

    def get_summary(self, obj_id: str) -> Dict[str, Any]:
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception as exc:
            DEFAULT_AUDIT_TRAIL.record("knowledge_summary_failed", {"id": obj_id, "error": str(exc)})
            raise MAXLegacyError(f"could not load knowledge object {obj_id}: {exc}")
        return {
            "id": obj.get("id"),
            "title": obj.get("title") or obj.get("name"),
            "type": obj.get("type"),
            "district": obj.get("district"),
            "icv": obj.get("icv"),
            "domain": obj.get("domain"),
        }

    def get_full(self, obj_id: str) -> Dict[str, Any]:
        try:
            obj = self.store.load_knowledge(obj_id)
            DEFAULT_AUDIT_TRAIL.record("knowledge_get_full", {"id": obj_id})
            return obj
        except Exception as exc:
            DEFAULT_AUDIT_TRAIL.record("knowledge_get_full_failed", {"id": obj_id, "error": str(exc)})
            raise

    def search_by_title(self, term: str) -> List[Dict[str, Any]]:
        if not term:
            return []
        term_low = term.lower()
        results: List[Dict[str, Any]] = []
        for p in self.store.knowledge_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                title = (data.get("title") or data.get("name") or "")
                if term_low in title.lower():
                    results.append({"id": data.get("id"), "title": title})
            except Exception:
                continue
        DEFAULT_AUDIT_TRAIL.record("knowledge_search", {"term": term, "count": len(results)})
        return results


