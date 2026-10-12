from __future__ import annotations

from typing import Dict, Any, List
from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime
from runtime.audit import DEFAULT_AUDIT_TRAIL


class ReportManager:
    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.mdt = MDTRuntime()
        self.qce = QCERuntime()
        try:
            self.qce.load_dependencies()
        except Exception:
            pass

    def customer_report(self, customer_id: str) -> Dict[str, Any]:
        # gather engagements, projects, and capability usage related to customer
        engagements = []
        projects = []
        for k in self.store.list_knowledge():
            try:
                obj = self.store.load_knowledge(k)
                if obj.get("type") in ("engagement", "revenue") and obj.get("customer_id") == customer_id:
                    engagements.append(obj)
                if obj.get("type") == "project" and obj.get("customer_id") == customer_id:
                    projects.append(obj)
            except Exception:
                continue
        # domain impacts via QCE
        affected = []
        if self.qce._deps:
            affected = self.qce.analyze_impact(["Umbrella"])[:10]
        DEFAULT_AUDIT_TRAIL.record("customer_report", {"customer_id": customer_id, "projects": len(projects), "engagements": len(engagements)})
        return {"customer_id": customer_id, "projects": projects, "engagements": engagements, "affected_domains": affected}
