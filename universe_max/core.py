"""Universe-Max core runtime.

Provides UniverseMax class which coordinates districts, ICVs, knowledge, simulation,
reality evaluation and view rendering. Designed to integrate with existing runtime
components (store, ICV registry) without introducing new architecture.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore
from icvs.manager import ICVManager


class UniverseMax:
    def __init__(self, store: Optional[Any] = None, icv_manager: Optional[Any] = None) -> None:
        self.store = store or MAXLegacyStore()
        self.icv_manager = icv_manager or ICVManager()
        # in-memory runtime context (can be persisted via store if available)
        self._context: Dict[str, Any] = {}

    # --- Loading helpers ---
    def load_district(self, district_name: str) -> Optional[Dict[str, Any]]:
        # Best-effort: delegate to store if it exposes district loading
        if hasattr(self.store, "load_district"):
            try:
                return self.store.load_district(district_name)
            except Exception:
                return None
        return None

    def load_icv(self, icv_name: str):
        return self.icv_manager.instantiate(icv_name)

    def load_knowledge(self, obj_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.store.load_knowledge(obj_id)
        except Exception:
            return None

    # --- Runtime operations ---
    def run_simulation(self, icv, obj_id: str) -> Dict[str, Any]:
        # Use the icv's analyze method as the simulation entry point.
        sim = {}
        try:
            analysis = icv.analyze(obj_id)
            sim["score"] = analysis.get("score") if analysis else None
            sim["analysis"] = analysis
        except Exception as e:
            sim["error"] = str(e)
        return {"simulation": sim}

    def evaluate_reality(self, icv, obj_id: str) -> Dict[str, Any]:
        # Evaluate reality via icv.alignment (preferred) and fallback to analysis
        res = {"alignment_score": None, "details": None}
        try:
            a = icv.alignment(obj_id)
            if isinstance(a, dict) and isinstance(a.get("score"), (int, float)):
                res["alignment_score"] = float(a.get("score"))
                res["details"] = a
            else:
                analysis = icv.analyze(obj_id)
                res["alignment_score"] = analysis.get("score") if analysis else None
                res["details"] = analysis
        except Exception as e:
            res["error"] = str(e)
        return {"reality_evaluation": res}

    def render_view(self, icv, obj_id: str) -> Dict[str, Any]:
        # Create a simple rendered view using knowledge and analysis
        view: Dict[str, Any] = {"id": obj_id}
        try:
            know = icv.knowledge(obj_id)
            view["title"] = know.get("title") if know else None
            view["body"] = know.get("body") or know.get("description") if know else None
            view["icv"] = icv.__class__.__name__
            view["analysis"] = icv.analyze(obj_id)
            view["alignment"] = icv.alignment(obj_id)
        except Exception as e:
            view["error"] = str(e)
        return {"view": view}

    # --- Context persistence (best-effort) ---
    def save_context(self, key: str, value: Any) -> bool:
        self._context[key] = value
        if hasattr(self.store, "save_context"):
            try:
                self.store.save_context(key, value)
                return True
            except Exception:
                return False
        return True

    def restore_context(self, key: str) -> Any:
        if key in self._context:
            return self._context[key]
        if hasattr(self.store, "load_context"):
            try:
                return self.store.load_context(key)
            except Exception:
                return None
        return None
