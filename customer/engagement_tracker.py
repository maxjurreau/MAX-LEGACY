"""Engagement tracker for Customer runtime."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict

from runtime.store import MAXLegacyStore


class EngagementTracker:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "customer" / "engagements"
        self.base.mkdir(parents=True, exist_ok=True)

    def track_engagement(self, customer_id: str, details: Dict[str, Any]) -> str:
        eid = f"ENG-{uuid.uuid4().hex[:8]}"
        obj = {"id": eid, "customer": customer_id, "details": details}
        p = self.base / f"{eid}.json"
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return eid
