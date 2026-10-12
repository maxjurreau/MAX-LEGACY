from __future__ import annotations

from typing import Any, Optional, Dict, List

from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime
from runtime.exceptions import MAXLegacyError


class BaseICV:
    """Base class for ICV modules.

    Provides lightweight access to runtime services. Concrete ICVs should
    override analyze(obj_id) and describe().

    New ICV contract methods (defaults provided):
    - identity(obj_id)
    - knowledge(obj_id)
    - history(obj_id)
    - alignment(obj_id)
    - recommendation(obj_id)
    - related_domains(obj_id)
    - related_knowledge(obj_id)
    - related_evidence(obj_id)
    """

    name: str = "base"

    def __init__(self, root: str | None = None) -> None:
        self.store = MAXLegacyStore(root=root)
        self.mdt = MDTRuntime()
        self.qce = QCERuntime()
        try:
            self.qce.load_dependencies()
        except Exception:
            # QCE best-effort; absence is tolerated
            pass

    def describe(self) -> str:
        return f"ICV={self.name}"

    def analyze(self, obj_id: str) -> Dict[str, Any] | None:
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

    # --- ICV contract defaults ---
    def identity(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """Return identity-related information for the object.

        Default: return entity_id and author fields when present.
        """
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return None
        return {"id": obj_id, "entity_id": obj.get("entity_id"), "author": obj.get("author")}

    def knowledge(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """Return the full knowledge object (read-only).
        """
        try:
            return self.store.load_knowledge(obj_id)
        except Exception:
            return None

    def history(self, obj_id: str) -> List[Dict[str, Any]]:
        """Return MDT timeline / history for the given object id.
        """
        try:
            return self.mdt.get_entity_history(obj_id)
        except Exception:
            return []

    def alignment(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """Return alignment information for the object, if any.
        """
        try:
            obj = self.store.load_knowledge(obj_id)
            return obj.get("alignment")
        except Exception:
            return None

    def recommendation(self, obj_id: str) -> Dict[str, Any]:
        """Produce a lightweight recommendation based on analyzed score.

        - score >= 0.7 -> promote
        - 0.4 <= score < 0.7 -> review
        - score < 0.4 or None -> recheck
        """
        analysis = self.analyze(obj_id) or {}
        score = analysis.get("score")
        if score is None:
            action = "recheck"
            reason = "no score available"
        elif score >= 0.7:
            action = "promote"
            reason = "high confidence"
        elif score >= 0.4:
            action = "review"
            reason = "moderate confidence"
        else:
            action = "recheck"
            reason = "low confidence"
        return {"id": obj_id, "action": action, "reason": reason, "score": score}

    def related_domains(self, obj_id: str) -> List[str]:
        """Return domains related to the object's domain using QCE.

        If QCE is unavailable, return an empty list.
        """
        try:
            obj = self.store.load_knowledge(obj_id)
            domain = obj.get("domain")
            if not domain:
                return []
            deps = []
            if hasattr(self.qce, "get_dependencies"):
                deps = self.qce.get_dependencies(domain) or []
            # also include dependents
            if hasattr(self.qce, "get_dependents"):
                deps += self.qce.get_dependents(domain) or []
            # deduplicate and sort
            return sorted(list(dict.fromkeys([d for d in deps if d])))
        except Exception:
            return []

    def related_knowledge(self, obj_id: str) -> List[Dict[str, Any]]:
        """Return lightweight list of related knowledge objects.

        Default heuristic: same domain or title substring match.
        """
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return []
        domain = obj.get("domain")
        title = (obj.get("title") or obj.get("name") or "").lower()
        related: List[Dict[str, Any]] = []
        for k in self.store.list_knowledge():
            try:
                candidate = self.store.load_knowledge(k)
            except Exception:
                continue
            if candidate.get("id") == obj_id:
                continue
            if domain and candidate.get("domain") == domain:
                related.append({"id": candidate.get("id"), "title": candidate.get("title") or candidate.get("name")})
                continue
            cand_title = (candidate.get("title") or candidate.get("name") or "").lower()
            if title and title in cand_title:
                related.append({"id": candidate.get("id"), "title": candidate.get("title") or candidate.get("name")})
        return related

    def related_evidence(self, obj_id: str) -> List[Dict[str, Any]]:
        """Return evidence items attached to the knowledge object.
        """
        try:
            obj = self.store.load_knowledge(obj_id)
        except Exception:
            return []
        ev = obj.get("evidence") or obj.get("evidences") or []
        if isinstance(ev, list):
            return ev
        if ev:
            return [ev]
        return []


