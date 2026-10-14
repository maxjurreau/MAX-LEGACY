"""Contract registry for Umbrella."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class ContractRegistry:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "umbrella" / "contracts"
        self.base.mkdir(parents=True, exist_ok=True)

    def record_contract(self, contract: Dict[str, Any]) -> str:
        cid = contract.get("id") or f"CT-{uuid.uuid4().hex[:8]}"
        data = dict(contract)
        data["id"] = cid
        path = self.base / f"{cid}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return cid

    def get_contract(self, cid: str) -> Optional[Dict[str, Any]]:
        p = self.base / f"{cid}.json"
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
