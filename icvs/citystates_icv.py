from __future__ import annotations

from .base import BaseICV


class CityStatesICV(BaseICV):
    name = "citystates"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # citystates ICV: attach geographic metadata where available
        try:
            obj = self.store.load_knowledge(obj_id)
            loc = obj.get("location") or obj.get("region")
            res["meta"]["location"] = loc
        except Exception:
            pass
        return res
