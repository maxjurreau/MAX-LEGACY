"""Capability usage tracker for Customer runtime."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict

from runtime.store import MAXLegacyStore


class CapabilityUsage:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "customer" / "usage"
        self.base.mkdir(parents=True, exist_ok=True)

    def record_usage(self, customer_id: str, capability_id: str, outcome: Dict[str, Any]) -> str:
        uid = f"U-{uuid.uuid4().hex[:8]}"
        obj = {"id": uid, "customer": customer_id, "capability": capability_id, "outcome": outcome}
        p = self.base / f"{uid}.json"
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return uid
