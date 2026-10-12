from __future__ import annotations

from .base import BaseICV


class ResearchICV(BaseICV):
    name = "research"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # lightweight heuristic: research objects with 'evidence' count get higher confidence
        try:
            obj = self.store.load_knowledge(obj_id)
            ev = obj.get("evidence") or obj.get("evidences") or []
            count = len(ev) if isinstance(ev, list) else 1 if ev else 0
            res["meta"]["evidence_count"] = count
            if res["score"] is None:
                res["score"] = min(0.1 * count + 0.5, 1.0)
        except Exception:
            pass
        return res
