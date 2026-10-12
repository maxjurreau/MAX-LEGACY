from __future__ import annotations

from typing import Dict, Any, List, Optional
from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime
from runtime.audit import DEFAULT_AUDIT_TRAIL


class CustomerManager:
    """Manage customers using the canonical MAXLegacyStore (no duplicate storage)."""

    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.engine = EventEngine(store=self.store)
        self.mdt = MDTRuntime()

    def create_customer(self, data: Dict[str, Any]) -> str:
        data = dict(data)
        data.setdefault("type", "customer")
        cid = self.store.save_knowledge(data)
        ev = self.engine.emit_event("customer.created", {"id": cid, **data})
        self.mdt.record_event(ev)
        DEFAULT_AUDIT_TRAIL.record("customer_created", {"id": cid})
        return cid

    def list_customers(self) -> List[str]:
        all_ids = []
        for k in self.store.list_knowledge():
            try:
                obj = self.store.load_knowledge(k)
                if obj.get("type") == "customer":
                    all_ids.append(k)
            except Exception:
                continue
        return sorted(all_ids)
