from __future__ import annotations

from .base import BaseICV


class MarketsICV(BaseICV):
    name = "markets"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # markets prefer 'prediction' with numeric expected value
        try:
            obj = self.store.load_knowledge(obj_id)
            pred = obj.get("prediction")
            if isinstance(pred, (int, float)):
                res["score"] = float(pred)
        except Exception:
            pass
        return res
