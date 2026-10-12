from __future__ import annotations

from typing import Dict, Any, List, Optional
from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime
from runtime.audit import DEFAULT_AUDIT_TRAIL


class CapabilityManager:
    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.engine = EventEngine(store=self.store)
        self.mdt = MDTRuntime()

    def register_capability(self, data: Dict[str, Any]) -> str:
        data = dict(data)
        data.setdefault("type", "capability")
        cid = self.store.save_knowledge(data)
        ev = self.engine.emit_event("capability.registered", {"id": cid, **data})
        self.mdt.record_event(ev)
        DEFAULT_AUDIT_TRAIL.record("capability_registered", {"id": cid})
        return cid

    def list_capabilities(self) -> List[str]:
        out = []
        for k in self.store.list_knowledge():
            try:
                obj = self.store.load_knowledge(k)
                if obj.get("type") == "capability":
                    out.append(k)
            except Exception:
                continue
        return sorted(out)
