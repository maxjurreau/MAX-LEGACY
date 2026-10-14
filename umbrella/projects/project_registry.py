"""Project registry for Umbrella."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

from runtime.store import MAXLegacyStore


class ProjectRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "umbrella" / "projects"
        self.base.mkdir(parents=True, exist_ok=True)

    def create_project(self, payload: Dict[str, Any]) -> str:
        pid = payload.get("id") or f"P-{uuid.uuid4().hex[:8]}"
        data = dict(payload)
        data.setdefault("capabilities", [])
        data["id"] = pid
        path = self.base / f"{pid}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return pid

    def add_capability(self, pid: str, capability_id: str) -> None:
        p = self.base / f"{pid}.json"
        if not p.exists():
            raise KeyError("project not found")
        data = json.loads(p.read_text(encoding="utf-8"))
        caps = data.get("capabilities", [])
        if capability_id not in caps:
            caps.append(capability_id)
        data["capabilities"] = caps
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_project(self, pid: str) -> Dict[str, Any]:
        p = self.base / f"{pid}.json"
        if not p.exists():
            raise KeyError("project not found")
        return json.loads(p.read_text(encoding="utf-8"))
