from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json

from runtime.store import MAXLegacyStore
from runtime.config import DEFAULT_CONFIG
from runtime.audit import DEFAULT_AUDIT_TRAIL


class ICVRegistry:
    """Registry for Individual Confidence Values (ICVs).

    This registry indexes ICVs that are embedded in knowledge objects under
    the key "icv". It is intentionally read-only and tolerant of malformed
    objects.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        repo_root = Path(root) if root is not None else DEFAULT_CONFIG.repo_root
        self.store = MAXLegacyStore(root=repo_root)
        self.knowledge_dir = self.store.knowledge_dir

    def list_icvs(self) -> List[str]:
        icvs = set()
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                icv = obj.get("icv")
                if icv:
                    if isinstance(icv, str):
                        icvs.add(icv)
                    elif isinstance(icv, dict) and "id" in icv:
                        icvs.add(str(icv["id"]))
            except Exception:
                continue
        DEFAULT_AUDIT_TRAIL.record("list_icvs", {"count": len(icvs)})
        return sorted(icvs)

    def get_icv_for_object(self, obj_id: str) -> Optional[Dict]:
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return None
        return obj.get("icv")

    def list_icv_objects(self, icv_id: str) -> List[Dict]:
        results: List[Dict] = []
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                icv = obj.get("icv")
                if isinstance(icv, str) and icv == icv_id:
                    results.append(obj)
                elif isinstance(icv, dict) and icv.get("id") == icv_id:
                    results.append(obj)
            except Exception:
                continue
        DEFAULT_AUDIT_TRAIL.record("list_icv_objects", {"icv": icv_id, "count": len(results)})
        return results


