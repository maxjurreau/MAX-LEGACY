"""Subscription registry for Revenue runtime."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class SubscriptionRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "revenue" / "subscriptions"
        self.base.mkdir(parents=True, exist_ok=True)

    def register_subscription(self, customer_id: str, plan: Dict[str, Any]) -> str:
        sid = f"S-{uuid.uuid4().hex[:8]}"
        obj = {"id": sid, "customer": customer_id, "plan": plan}
        p = self.base / f"{sid}.json"
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return sid
