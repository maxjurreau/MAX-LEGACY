from __future__ import annotations

from typing import Any, Optional

from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime


class BaseICV:
    """Base class for ICV modules.

    Provides lightweight access to runtime services. Concrete ICVs should
    override analyze(obj_id) and describe().
    """

    name: str = "base"

    def __init__(self, root: str | None = None) -> None:
        self.store = MAXLegacyStore(root=root)
        self.mdt = MDTRuntime()
        self.qce = QCERuntime()
        try:
            self.qce.load_dependencies()
        except Exception:
            pass

    def describe(self) -> str:
        return f"ICV={self.name}"

    def analyze(self, obj_id: str) -> dict[str, Any] | None:
        """Analyze a knowledge object and return a dict with insights.

        Default implementation attempts to load stored 'icv' or 'alignment' and
        returns a simple score. Concrete classes should override for domain logic.
        """
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return None
        # prefer explicit icv value
        icv = obj.get("icv")
        alignment = obj.get("alignment")
        score: Optional[float] = None
        if isinstance(icv, (int, float)):
            score = float(icv)
        elif isinstance(icv, dict) and isinstance(icv.get("score"), (int, float)):
            score = float(icv.get("score"))
        elif isinstance(alignment, dict) and isinstance(alignment.get("score"), (int, float)):
            score = float(alignment.get("score"))
        return {"id": obj_id, "icv_name": self.name, "score": score, "meta": {"title": obj.get("title") or obj.get("name")}} 
