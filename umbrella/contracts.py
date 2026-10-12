from __future__ import annotations

from typing import Dict, Any, List, Optional
from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime
from runtime.audit import DEFAULT_AUDIT_TRAIL


class ContractManager:
    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.engine = EventEngine(store=self.store)
        self.mdt = MDTRuntime()

    def create_contract(self, data: Dict[str, Any]) -> str:
        data = dict(data)
        data.setdefault("type", "contract")
        cid = self.store.save_knowledge(data)
        ev = self.engine.emit_event("contract.created", {"id": cid, **data})
        self.mdt.record_event(ev)
        DEFAULT_AUDIT_TRAIL.record("contract_created", {"id": cid})
        return cid

    def list_contracts(self) -> List[str]:
        out = []
        for k in self.store.list_knowledge():
            try:
                obj = self.store.load_knowledge(k)
                if obj.get("type") == "contract":
                    out.append(k)
            except Exception:
                continue
        return sorted(out)
