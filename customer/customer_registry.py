"""Customer runtime components."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class CustomerRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "customer" / "customers"
        self.base.mkdir(parents=True, exist_ok=True)

    def register_customer(self, payload: Dict[str, Any]) -> str:
        cid = payload.get("id") or f"CUST-{uuid.uuid4().hex[:8]}"
        data = dict(payload)
        data["id"] = cid
        p = self.base / f"{cid}.json"
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return cid

    def get_customer(self, cid: str) -> Optional[Dict[str, Any]]:
        p = self.base / f"{cid}.json"
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
