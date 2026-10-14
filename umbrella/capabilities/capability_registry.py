"""Capability registry for Umbrella."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

from runtime.store import MAXLegacyStore


class CapabilityRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "umbrella" / "capabilities"
        self.base.mkdir(parents=True, exist_ok=True)

    def register_capability(self, spec: Dict[str, Any]) -> str:
        cid = spec.get("id") or f"CAP-{uuid.uuid4().hex[:8]}"
        data = dict(spec)
        data["id"] = cid
        path = self.base / f"{cid}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return cid

    def list_all(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for p in self.base.glob("*.json"):
            out.append(json.loads(p.read_text(encoding="utf-8")))
        return out
