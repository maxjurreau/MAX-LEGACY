"""Umbrella runtime: capability delivery layer."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime
from runtime.event_engine import EventEngine

from .customers.customer_registry import CustomerRegistry
from .projects.project_registry import ProjectRegistry
from .capabilities.capability_registry import CapabilityRegistry
from .contracts.contract_registry import ContractRegistry
from .revenue.revenue_registry import RevenueRegistry
from .reports.reporting import ReportingEngine


class UmbrellaRuntime:
    """Capability delivery orchestration for Umbrella.

    Responsibilities:
    - track customers, projects, capabilities, contracts and revenue
    - expose simple CRUD and record APIs used by higher-level flows
    """

    def __init__(
        self,
        store: Optional[MAXLegacyStore] = None,
        mdt: Optional[MDTRuntime] = None,
        event_engine: Optional[EventEngine] = None,
    ) -> None:
        self.store = store or MAXLegacyStore()
        self.mdt = mdt or MDTRuntime()
        self.event_engine = event_engine or EventEngine(store=self.store)

        # registries
        self.customers = CustomerRegistry(self.store)
        self.projects = ProjectRegistry(self.store)
        self.capabilities = CapabilityRegistry(self.store)
        self.contracts = ContractRegistry(self.store)
        self.revenue = RevenueRegistry(self.store)
        self.reporting = ReportingEngine(self.store)

    # customer/project/capability lifecycle
    def create_customer(self, payload: Dict[str, Any]) -> str:
        cid = self.customers.register_customer(payload)
        self.mdt.record_event({"type": "customer_created", "id": cid})
        self.event_engine.emit_event("customer_created", {"id": cid, "payload": payload})
        return cid

    def create_project(self, payload: Dict[str, Any]) -> str:
        pid = self.projects.create_project(payload)
        self.mdt.record_event({"type": "project_created", "id": pid})
        self.event_engine.emit_event("project_created", {"id": pid, "payload": payload})
        return pid

    def assign_capability(self, project_id: str, capability_spec: Dict[str, Any]) -> str:
        cap_id = self.capabilities.register_capability(capability_spec)
        self.projects.add_capability(project_id, cap_id)
        self.mdt.record_event({"type": "capability_assigned", "project": project_id, "capability": cap_id})
        self.event_engine.emit_event("capability_assigned", {"project": project_id, "capability": cap_id})
        return cap_id

    # contracts and revenue
    def record_contract(self, contract: Dict[str, Any]) -> str:
        cid = self.contracts.record_contract(contract)
        self.mdt.record_event({"type": "contract_recorded", "id": cid})
        return cid

    def record_revenue(self, revenue_event: Dict[str, Any]) -> str:
        rid = self.revenue.record_revenue(revenue_event)
        self.mdt.record_event({"type": "revenue_recorded", "id": rid})
        self.event_engine.emit_event("revenue_recorded", revenue_event)
        return rid

    def record_evidence(self, evidence: Dict[str, Any]) -> str:
        # evidence recorded as a lightweight knowledge artifact in umbrella area
        base = Path(self.store.root) / "umbrella" / "evidence"
        base.mkdir(parents=True, exist_ok=True)
        eid = evidence.get("id") or f"E-{uuid.uuid4().hex[:8]}"
        path = base / f"{eid}.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.mdt.record_event({"type": "evidence_recorded", "id": eid})
        return eid

    def generate_report(self, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # delegate to reporting engine
        return self.reporting.generate_report(scope)

    def list_capabilities(self) -> List[Dict[str, Any]]:
        return self.capabilities.list_all()
