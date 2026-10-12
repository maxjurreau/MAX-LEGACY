from __future__ import annotations

from .base import BaseICV


class RealityICV(BaseICV):
    name = "reality"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # if alignment present, prefer it
        try:
            obj = self.store.load_knowledge(obj_id)
            a = obj.get("alignment")
            if isinstance(a, dict) and isinstance(a.get("score"), (int, float)):
                res["score"] = float(a["score"]) 
        except Exception:
            pass
        return res
