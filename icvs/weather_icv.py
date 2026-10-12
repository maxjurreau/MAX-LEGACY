from __future__ import annotations

from .base import BaseICV


class WeatherICV(BaseICV):
    name = "weather"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # weather ICVs use 'confidence' or 'probability' fields
        try:
            obj = self.store.load_knowledge(obj_id)
            p = obj.get("probability") or obj.get("confidence")
            if isinstance(p, (int, float)):
                res["score"] = float(p)
        except Exception:
            pass
        return res
