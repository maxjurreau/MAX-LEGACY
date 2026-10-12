from __future__ import annotations

from .base import BaseICV


class HealthICV(BaseICV):
    name = "health"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # health ICVs check for clinical evidence markers
        try:
            obj = self.store.load_knowledge(obj_id)
            markers = obj.get("clinical_evidence") or obj.get("evidence")
            if markers:
                if res["score"] is None:
                    res["score"] = 0.6
        except Exception:
            pass
        return res
