"""Audit trail helpers for MAX-LEGACY runtime."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditTrail:
    """Simple append-only audit log for runtime events and validator outcomes."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else Path(__file__).resolve().parent / "audit_log.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def record(self, event_type: str, payload: dict[str, Any] | None = None, **metadata: Any) -> dict[str, Any]:
        entry = {
            "timestamp": self._now(),
            "type": event_type,
            "payload": payload or {},
        }
        if metadata:
            entry.update(metadata)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")
        return entry

    def read_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        entries: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entries.append(json.loads(line))
                if len(entries) >= limit:
                    break
        return entries


DEFAULT_AUDIT_TRAIL = AuditTrail()
