from __future__ import annotations

from .base import BaseICV


class LawICV(BaseICV):
    name = "law"

    def analyze(self, obj_id: str):
        res = super().analyze(obj_id)
        if res is None:
            return None
        # law ICVs are conservative: lower default score
        if res.get("score") is None:
            res["score"] = 0.4
        return res
