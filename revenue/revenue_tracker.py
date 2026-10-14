"""Revenue runtime: recording and invoicing."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class RevenueTracker:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "revenue" / "events"
        self.base.mkdir(parents=True, exist_ok=True)

    def record_revenue(self, event: Dict[str, Any]) -> str:
        rid = event.get("id") or f"REV-{uuid.uuid4().hex[:8]}"
        data = dict(event)
        data["id"] = rid
        p = self.base / f"{rid}.json"
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return rid


class InvoiceEngine:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "revenue" / "invoices"
        self.base.mkdir(parents=True, exist_ok=True)

    def create_invoice(self, customer_id: str, items: list[Dict[str, Any]]) -> str:
        invoice_id = f"INV-{uuid.uuid4().hex[:8]}"
        total = sum(float(i.get("amount", 0.0)) for i in items)
        obj = {"id": invoice_id, "customer": customer_id, "items": items, "total": total}
        p = self.base / f"{invoice_id}.json"
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return invoice_id
