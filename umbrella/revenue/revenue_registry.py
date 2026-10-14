"""Revenue registry used by Umbrella."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class RevenueRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "umbrella" / "revenue"
        self.base.mkdir(parents=True, exist_ok=True)

    def record_revenue(self, event: Dict[str, Any]) -> str:
        rid = event.get("id") or f"R-{uuid.uuid4().hex[:8]}"
        data = dict(event)
        data["id"] = rid
        path = self.base / f"{rid}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return rid

    def list_revenue(self) -> list[Dict[str, Any]]:
        out = []
        for p in self.base.glob("*.json"):
            out.append(json.loads(p.read_text(encoding="utf-8")))
        return out
