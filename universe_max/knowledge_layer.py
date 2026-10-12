from __future__ import annotations

from typing import Dict, Any, List
from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime


class KnowledgeLayer:
    """Proxy to MAXLegacyStore that also emits events and records MDT traces.

    This ensures there is a single canonical store and an event path for all
    knowledge operations.
    """

    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.engine = EventEngine(store=self.store)
        self.mdt = MDTRuntime()

    def create_knowledge(self, obj: Dict[str, Any]) -> str:
        kid = self.store.save_knowledge(obj)
        ev = self.engine.emit_event("knowledge.create", {"id": kid, **obj})
        self.mdt.record_event(ev)
        return kid

    def list_objects(self) -> List[str]:
        return self.store.list_knowledge()
