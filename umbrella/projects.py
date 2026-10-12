from __future__ import annotations

from typing import Dict, Any, List, Optional
from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime
from runtime.audit import DEFAULT_AUDIT_TRAIL


class ProjectManager:
    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.engine = EventEngine(store=self.store)
        self.mdt = MDTRuntime()

    def create_project(self, data: Dict[str, Any]) -> str:
        data = dict(data)
        data.setdefault("type", "project")
        pid = self.store.save_knowledge(data)
        ev = self.engine.emit_event("project.created", {"id": pid, **data})
        self.mdt.record_event(ev)
        DEFAULT_AUDIT_TRAIL.record("project_created", {"id": pid})
        return pid

    def list_projects(self) -> List[str]:
        out = []
        for k in self.store.list_knowledge():
            try:
                obj = self.store.load_knowledge(k)
                if obj.get("type") == "project":
                    out.append(k)
            except Exception:
                continue
        return sorted(out)
