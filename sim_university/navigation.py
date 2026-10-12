from __future__ import annotations

from typing import Dict, List, Any, Optional
from pathlib import Path

from .district_registry import DistrictRegistry
from .icv_registry import ICVRegistry
from sim_university.knowledge_views import KnowledgeViews
from sim_university.reality_views import RealityViews
from runtime.mdt import MDTRuntime
from runtime.config import DEFAULT_CONFIG
from runtime.audit import DEFAULT_AUDIT_TRAIL
from runtime.exceptions import DomainNotFoundError


class Navigation:
    """Generate navigable views and simple navigation operations.

    This class is lightweight and designed to be used by UI or API layers to
    allow users to explore districts, ICVs, and knowledge objects.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        repo_root = Path(root) if root is not None else DEFAULT_CONFIG.repo_root
        self.districts = DistrictRegistry(root=repo_root)
        self.icvs = ICVRegistry(root=repo_root)
        self.knowledge = KnowledgeViews(root=repo_root)
        self.reality = RealityViews(root=repo_root)
        self.mdt = MDTRuntime()

    # ----- index operations -----
    def list_districts(self) -> List[str]:
        return self.districts.list_districts()

    def list_icvs(self) -> List[str]:
        return self.icvs.list_icvs()

    # ----- navigation -----
    def enter_district(self, district_id: str) -> Dict[str, Any]:
        """Enter a district and return basic context for UI rendering."""
        if district_id not in self.districts.list_districts():
            raise DomainNotFoundError(f"district not found: {district_id}")
        objs = self.districts.get_district_knowledge(district_id)
        summary = {"district": district_id, "count": len(objs), "objects": []}
        for o in objs:
            summary["objects"].append({"id": o.get("id"), "title": o.get("title") or o.get("name")})
        DEFAULT_AUDIT_TRAIL.record("enter_district", {"district": district_id, "count": len(objs)})
        return summary

    def leave_district(self, district_id: str) -> Dict[str, Any]:
        # No persistent session model here; record for audit and return simple ack
        DEFAULT_AUDIT_TRAIL.record("leave_district", {"district": district_id})
        return {"status": "left", "district": district_id}

    # ----- object and evidence views -----
    def view_knowledge(self, obj_id: str) -> Dict[str, Any]:
        try:
            s = self.knowledge.get_summary(obj_id)
            DEFAULT_AUDIT_TRAIL.record("view_knowledge", {"id": obj_id})
            return s
        except Exception as exc:
            DEFAULT_AUDIT_TRAIL.record("view_knowledge_failed", {"id": obj_id, "error": str(exc)})
            raise

    def view_evidence(self, obj_id: str) -> Dict[str, Any]:
        try:
            obj = self.knowledge.store.load_knowledge(obj_id)
            ev = obj.get("evidence") or obj.get("evidences") or []
            DEFAULT_AUDIT_TRAIL.record("view_evidence", {"id": obj_id, "count": len(ev) if isinstance(ev, list) else 1})
            return {"id": obj_id, "evidence": ev}
        except Exception:
            DEFAULT_AUDIT_TRAIL.record("view_evidence_failed", {"id": obj_id})
            return {"id": obj_id, "evidence": None}

    # ----- reality and domain history -----
    def view_reality_alignment(self, obj_id: str) -> Dict[str, Any]:
        res = self.reality.object_alignment(obj_id)
        DEFAULT_AUDIT_TRAIL.record("view_reality_alignment", {"id": obj_id, "alignment": res.get("alignment")})
        return res

    def view_domain_history(self, district_id: str) -> List[Dict[str, Any]]:
        # MDT stores domain history keyed by domain/district. We return a copy.
        history = self.mdt.get_domain_history(district_id)
        DEFAULT_AUDIT_TRAIL.record("view_domain_history", {"district": district_id, "entries": len(history)})
        return history

    # ----- high level helpers -----
    def navigable_tree(self) -> Dict[str, Any]:
        tree = {"districts": []}
        for d in self.list_districts():
            objs = self.districts.get_district_knowledge(d)
            tree["districts"].append({
                "district": d,
                "count": len(objs),
                "objects": [{"id": o.get("id"), "title": o.get("title") or o.get("name")} for o in objs],
            })
        return tree

    def navigate_between(self, from_district: str, to_district: str) -> Dict[str, Any]:
        if from_district not in self.list_districts() or to_district not in self.list_districts():
            raise DomainNotFoundError("source or destination district not found")
        DEFAULT_AUDIT_TRAIL.record("navigate_between", {"from": from_district, "to": to_district})
        # The navigation model is simple: return destination context
        return self.enter_district(to_district)


