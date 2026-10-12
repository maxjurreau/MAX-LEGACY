import os
import json
import uuid
from datetime import datetime


class MDTRuntime:
    """MDT runtime integrated with an EventEngine-like interface.

    Responsibilities:
    - Validate events before persisting (basic shape checks)
    - Persist events, changes, promotions, domain updates
    - Expose timeline and history queries
    """

    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = os.path.join("runtime", "_mdt_store.json")
        self.storage_path = storage_path
        self._data = {
            "events": [],
            "changes": [],
            "promotions": [],
            "domain_updates": [],
            "timeline_by_entity": {},
            "domain_history": {},
        }
        self._load()

    def _load(self):
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            d = os.path.dirname(self.storage_path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            self._save()

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)

    def _now(self):
        return datetime.utcnow().isoformat() + "Z"

    def _validate_event(self, event: dict) -> None:
        # Basic validation: must have type and data
        if not isinstance(event, dict):
            raise ValueError("event must be a dict")
        if "type" not in event:
            raise ValueError("event missing type")
        if "data" not in event:
            raise ValueError("event missing data")

    def _register_in_timeline(self, entity_id, record):
        if not entity_id:
            return
        tl = self._data["timeline_by_entity"].setdefault(entity_id, [])
        tl.append(record)

    def record_change(self, change: dict) -> str:
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

    def record_event(self, event: dict) -> str:
        """Record an event after validation."""
        self._validate_event(event)
        event = dict(event)
        if "id" not in event:
            event["id"] = f"EV-{uuid.uuid4().hex[:8]}"
        event.setdefault("timestamp", self._now())
        self._data["events"].append(event)
        # timeline
        entity_id = event.get("entity_id") or (event.get("data") or {}).get("id")
        self._register_in_timeline(entity_id, {"type": "event", "id": event["id"], "event": event})
        domain = event.get("domain") or (event.get("data") or {}).get("domain")
        if domain:
            self._data["domain_history"].setdefault(domain, []).append(event)
        self._save()
        return event["id"]

    def record_promotion(self, promotion: dict) -> str:
        promotion = dict(promotion)
        promotion.setdefault("id", f"PROM-{uuid.uuid4().hex[:8]}")
        promotion.setdefault("timestamp", self._now())
        # basic validation
        if "entity_id" not in promotion:
            raise ValueError("promotion must reference entity_id")
        self._data["promotions"].append(promotion)
        entity_id = promotion.get("entity_id")
        self._register_in_timeline(entity_id, {"type": "promotion", "id": promotion["id"], "promotion": promotion})
        self._save()
        return promotion["id"]

    def record_domain_update(self, update: dict) -> str:
        update = dict(update)
        update.setdefault("id", f"DUP-{uuid.uuid4().hex[:8]}")
        update.setdefault("timestamp", self._now())
        domain = update.get("domain")
        if domain:
            self._data["domain_history"].setdefault(domain, []).append(update)
        self._data["domain_updates"].append(update)
        self._save()
        return update["id"]

    def get_timeline(self, entity_id: str) -> list:
        return list(self._data["timeline_by_entity"].get(entity_id, []))

    def get_entity_history(self, entity_id: str) -> list:
        items = []
        for e in self._data["events"]:
            if e.get("entity_id") == entity_id or (e.get("data") or {}).get("id") == entity_id:
                items.append(e)
        for c in self._data["changes"]:
            if c.get("entity_id") == entity_id:
                items.append(c)
        for p in self._data["promotions"]:
            if p.get("entity_id") == entity_id:
                items.append(p)
        items.sort(key=lambda x: x.get("timestamp", ""))
        return items

    def get_domain_history(self, domain: str) -> list:
        return list(self._data["domain_history"].get(domain, []))
