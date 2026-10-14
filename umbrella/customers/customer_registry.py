"""Customer registry for Umbrella."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class CustomerRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "umbrella" / "customers"
        self.base.mkdir(parents=True, exist_ok=True)

    def register_customer(self, payload: Dict[str, Any]) -> str:
        cid = payload.get("id") or f"C-{uuid.uuid4().hex[:8]}"
        payload = dict(payload)
        payload["id"] = cid
        path = self.base / f"{cid}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return cid

    def get_customer(self, cid: str) -> Optional[Dict[str, Any]]:
        path = self.base / f"{cid}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
