import os
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List


class MDTRuntime:
    """MAX Domain Tracker (MDT) for Runtime v1.0

    Tracks changes, events, promotions, and domain updates.
    Persists state to runtime/_mdt_store.json for integration and tests.
    """

    def __init__(self, storage_path: str | None = None):
        if storage_path is None:
            storage_path = os.path.join("runtime", "_mdt_store.json")
        self.storage_path = storage_path
        self._data: Dict[str, Any] = {
            "events": [],
            "changes": [],
            "promotions": [],
            "domain_updates": [],
            "timeline_by_entity": {},
            "domain_history": {},
        }
        self._load()

    def _load(self) -> None:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            d = os.path.dirname(self.storage_path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            self._save()

    def _save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _register_in_timeline(self, entity_id: str | None, record: Dict[str, Any]) -> None:
        if not entity_id:
            return
        tl = self._data["timeline_by_entity"].setdefault(entity_id, [])
        tl.append(record)

    def record_change(self, change: Dict[str, Any]) -> str:
        change = dict(change)
        change.setdefault("id", f"CHG-{uuid.uuid4().hex[:8]}")
        change.setdefault("timestamp", self._now())
        self._data["changes"].append(change)
        entity_id = change.get("entity_id")
        self._register_in_timeline(entity_id, {"type": "change", "id": change["id"], "change": change})
        domain = change.get("domain")
        if domain:
            self._data["domain_history"].setdefault(domain, []).append(change)
        self._save()
        return change["id"]

    def record_event(self, event: Dict[str, Any]) -> str:
        # Basic validation here: event must have id and type
        if not isinstance(event, dict):
            raise ValueError("event must be a dict")
        if "type" not in event:
            raise ValueError("event missing type")
        if "id" not in event:
            raise ValueError("event must include id before MDT record")
        event = dict(event)
        event.setdefault("timestamp", self._now())
        self._data["events"].append(event)
        entity_id = event.get("entity_id") or (event.get("payload") or {}).get("id") or (event.get("data") or {}).get("id")
        self._register_in_timeline(entity_id, {"type": "event", "id": event["id"], "event": event})
        domain = event.get("domain") or (event.get("payload") or {}).get("domain") or (event.get("data") or {}).get("domain")
        if domain:
            self._data["domain_history"].setdefault(domain, []).append(event)
        self._save()
        return event["id"]

    def record_promotion(self, promotion: Dict[str, Any]) -> str:
        promotion = dict(promotion)
        promotion.setdefault("id", f"PROM-{uuid.uuid4().hex[:8]}")
        promotion.setdefault("timestamp", self._now())
        if "entity_id" not in promotion:
            raise ValueError("promotion must reference entity_id")
        self._data["promotions"].append(promotion)
        entity_id = promotion.get("entity_id")
        self._register_in_timeline(entity_id, {"type": "promotion", "id": promotion["id"], "promotion": promotion})
        self._save()
        return promotion["id"]

    def record_domain_update(self, update: Dict[str, Any]) -> str:
        update = dict(update)
        update.setdefault("id", f"DUP-{uuid.uuid4().hex[:8]}")
        update.setdefault("timestamp", self._now())
        domain = update.get("domain")
        if domain:
            self._data["domain_history"].setdefault(domain, []).append(update)
        self._data["domain_updates"].append(update)
        self._save()
        return update["id"]

    def get_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        return list(self._data["timeline_by_entity"].get(entity_id, []))

    def get_entity_history(self, entity_id: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for e in self._data.get("events", []):
            if e.get("entity_id") == entity_id or (e.get("payload") or {}).get("id") == entity_id or (e.get("data") or {}).get("id") == entity_id:
                items.append(e)
        for c in self._data.get("changes", []):
            if c.get("entity_id") == entity_id:
                items.append(c)
        for p in self._data.get("promotions", []):
            if p.get("entity_id") == entity_id:
                items.append(p)
        items.sort(key=lambda x: x.get("timestamp", ""))
        return items

    def get_domain_history(self, domain: str) -> List[Dict[str, Any]]:
        return list(self._data["domain_history"].get(domain, []))
