from __future__ import annotations

from typing import Dict, List, Any
from pathlib import Path
import json

from runtime.store import MAXLegacyStore


class RealityViews:
    """Compute simple reality-alignment metrics for districts and objects.

    This layer is intentionally light-weight for v0.1 and uses fields embedded in
    knowledge objects (e.g., "alignment": {"score": float}) as the source of truth.
    """

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
        self.store = MAXLegacyStore(root=self.root)

    def object_alignment(self, obj_id: str) -> Dict[str, Any]:
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return {"id": obj_id, "alignment": None}
        alignment = obj.get("alignment")
        return {"id": obj_id, "alignment": alignment}

    def district_alignment(self, district_id: str) -> Dict[str, Any]:
        # aggregate alignment scores for district objects
        results = []
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
            return {"district": district_id, "count": 0, "average_score": None}
        avg = sum(results) / len(results)
        return {"district": district_id, "count": len(results), "average_score": avg}


