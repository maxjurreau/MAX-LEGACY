from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
from pathlib import Path

from .store import MAXLegacyStore


@dataclass
class EventEngine:
    """Event engine that validates events against a local schema and persists via MAXLegacyStore.

    Validation strategy:
    - If schema/event.schema.json exists, use its "required" list to ensure fields are present.
      This is a lightweight validator (no external jsonschema dependency).
    - If not present, enforce a conservative builtin schema requiring: type, payload, timestamp.

    ID generation is delegated to the store which produces deterministic EV-XXXX ids.
    """

    store: MAXLegacyStore
    schema: Optional[Dict[str, Any]] = None

    def _schema_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "schema" / "event.schema.json"

    def _load_schema(self) -> None:
        if self.schema is not None:
            return
        p = self._schema_path()
        if not p.exists():
            self.schema = None
            return
        try:
            self.schema = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            self.schema = None

    def validate_event(self, event: Dict[str, Any]) -> None:
        self._load_schema()
        # Basic checks
        if not isinstance(event, dict):
            raise ValueError("event must be an object")
        # If schema present, use its 'required' if available
        if self.schema and isinstance(self.schema.get("required"), list):
            for key in self.schema["required"]:
                if key not in event:
                    raise ValueError(f"event missing required field: {key}")
        else:
            # fallback checks
            for key in ("type", "payload", "timestamp"):
                if key not in event:
                    raise ValueError(f"event missing required field: {key}")

    def next_event_id(self) -> str:
        """Return the next event id without persisting anything."""
        return self.store._next_event_id()

    def emit_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event: Dict[str, Any] = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        # validate against schema
        self.validate_event(event)
        # persist, store will allocate deterministic EV-XXXX id
        event_id = self.store.save_event(event)
        event["id"] = event_id
        return event

    def emit_promotion_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.emit_event("promotion", payload)

    def emit_validation_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.emit_event("validation", payload)
