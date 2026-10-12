from __future__ import annotations

from .base import BaseICV


class SportsICV(BaseICV):
    name = "sports"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # sports predictions may include 'odds' or 'confidence' fields
        try:
            obj = self.store.load_knowledge(obj_id)
            if isinstance(obj.get("odds"), (int, float)):
                res["score"] = float(obj.get("odds"))
        except Exception:
            pass
        return res
