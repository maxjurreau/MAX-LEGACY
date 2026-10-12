from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json

from runtime.store import MAXLegacyStore


class ICVRegistry:
    """Registry for Individual Confidence Values (ICVs) or similar metrics.

    ICVs are expected to be attached to knowledge objects under the key "icv".
    This registry provides a simple index and listing.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        if root is None:
            root = Path(__file__).resolve().parents[1]
        self.root = Path(root)
        self.store = MAXLegacyStore(root=self.root)
        self.knowledge_dir = self.store.knowledge_dir

    def list_icvs(self) -> List[str]:
        icvs = set()
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                icv = obj.get("icv")
                if icv:
                    # allow icv to be either id or named tag
                    if isinstance(icv, str):
                        icvs.add(icv)
                    elif isinstance(icv, dict) and "id" in icv:
                        icvs.add(icv["id"])
            except Exception:
                continue
        return sorted(icvs)

    def get_icv_for_object(self, obj_id: str) -> Optional[Dict]:
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return None
        return obj.get("icv")

    def list_icv_objects(self, icv_id: str) -> List[Dict]:
        results = []
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
        return results


