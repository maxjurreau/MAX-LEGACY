from __future__ import annotations

from .base import BaseICV


class EconomicsICV(BaseICV):
    name = "economics"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # economics ICVs may use 'expected_value'
        try:
            obj = self.store.load_knowledge(obj_id)
            ev = obj.get("expected_value")
            if isinstance(ev, (int, float)):
                res["score"] = float(ev)
        except Exception:
            pass
        return res
