"""Reporting helpers for Umbrella."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.store import MAXLegacyStore


class ReportingEngine:
    def __init__(self, store: MAXLegacyStore) -> None:
        self.store = store
        self.base = Path(self.store.root) / "umbrella" / "reports"
        self.base.mkdir(parents=True, exist_ok=True)

    def generate_report(self, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # simple aggregate report
        out: Dict[str, Any] = {"customers": 0, "projects": 0, "capabilities": 0, "revenue": 0.0}
        cust_dir = Path(self.store.root) / "umbrella" / "customers"
        proj_dir = Path(self.store.root) / "umbrella" / "projects"
        cap_dir = Path(self.store.root) / "umbrella" / "capabilities"
        rev_dir = Path(self.store.root) / "umbrella" / "revenue"
        out["customers"] = len(list(cust_dir.glob("*.json"))) if cust_dir.exists() else 0
        out["projects"] = len(list(proj_dir.glob("*.json"))) if proj_dir.exists() else 0
        out["capabilities"] = len(list(cap_dir.glob("*.json"))) if cap_dir.exists() else 0
        # sum revenue
        total = 0.0
        if rev_dir.exists():
            for p in rev_dir.glob("*.json"):
                try:
                    obj = json.loads(p.read_text(encoding="utf-8"))
                    total += float(obj.get("amount", 0.0))
                except Exception:
                    continue
        out["revenue"] = total
        return out
