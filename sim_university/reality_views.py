from __future__ import annotations

from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from runtime.store import MAXLegacyStore
from runtime.config import DEFAULT_CONFIG
from runtime.audit import DEFAULT_AUDIT_TRAIL


class RealityViews:
    """Compute simple reality-alignment metrics for districts and objects.

    This layer reads 'alignment' fields embedded in knowledge objects and
    aggregates them. It intentionally avoids introducing new reality scoring
    schemas; it uses stored content as-is.
    """

    def __init__(self, root: Optional[Path] = None):
        repo_root = Path(root) if root is not None else DEFAULT_CONFIG.repo_root
        self.store = MAXLegacyStore(root=repo_root)

    def object_alignment(self, obj_id: str) -> Dict[str, Any]:
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            DEFAULT_AUDIT_TRAIL.record("object_alignment_missing", {"id": obj_id})
            return {"id": obj_id, "alignment": None}
        alignment = obj.get("alignment")
        DEFAULT_AUDIT_TRAIL.record("object_alignment_view", {"id": obj_id, "alignment": alignment})
        return {"id": obj_id, "alignment": alignment}

    def district_alignment(self, district_id: str) -> Dict[str, Any]:
        results: List[float] = []
        for p in self.store.knowledge_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("district") == district_id:
                    a = data.get("alignment")
                    if isinstance(a, dict) and "score" in a:
                        results.append(float(a["score"]))
                    elif isinstance(a, (int, float)):
                        results.append(float(a))
            except Exception:
                continue
        if not results:
            DEFAULT_AUDIT_TRAIL.record("district_alignment_empty", {"district": district_id})
            return {"district": district_id, "count": 0, "average_score": None}
        avg = sum(results) / len(results)
        DEFAULT_AUDIT_TRAIL.record("district_alignment", {"district": district_id, "count": len(results), "average": avg})
        return {"district": district_id, "count": len(results), "average_score": avg}


