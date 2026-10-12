from __future__ import annotations

from .base import BaseICV


class LearningICV(BaseICV):
    name = "learning"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # learning ICVs favor objects with examples/training_count
        try:
            obj = self.store.load_knowledge(obj_id)
            tc = obj.get("training_count") or obj.get("examples")
            if isinstance(tc, int) and tc > 0 and res.get("score") is None:
                res["score"] = min(0.5 + 0.01 * tc, 1.0)
        except Exception:
            pass
        return res
