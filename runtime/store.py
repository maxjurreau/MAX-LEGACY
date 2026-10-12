from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


K_PATTERN = re.compile(r"^K-\d{3}$")
EV_PATTERN = re.compile(r"^EV-\d{4}$")


class MAXLegacyStore:
    """Filesystem-backed deterministic store for MAX-LEGACY runtime.

    - knowledge objects are stored under <repo_root>/knowledge as JSON files named <id>.json
    - events are stored under <repo_root>/events as JSON files named <id>.json

    ID generation is deterministic: the next numeric suffix is derived from
    existing files using a stable numeric parse (max(existing)+1).
    Knowledge IDs use 3 digits (K-###). Event IDs use 4 digits (EV-####).
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        if root is None:
            root = Path(__file__).resolve().parents[1]
        self.root: Path = Path(root)
        self.knowledge_dir = self.root / "knowledge"
        self.events_dir = self.root / "events"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

    # ---- knowledge API ----
    def _next_knowledge_id(self) -> str:
        existing = [p.stem for p in self.knowledge_dir.glob("*.json") if p.is_file()]
        nums: List[int] = []
        for name in existing:
            if name.startswith("K-"):
                try:
                    nums.append(int(name.split("-", 1)[1]))
                except Exception:
                    continue
        next_num = (max(nums) + 1) if nums else 1
        return f"K-{next_num:03d}"

    def save_knowledge(self, obj: Dict[str, Any]) -> str:
        obj = dict(obj)
        provided_id = obj.get("id")
        if provided_id is not None:
            if not isinstance(provided_id, str) or not K_PATTERN.match(provided_id):
                raise ValueError("knowledge id must match format K-XXX (e.g. K-001)")
            obj_id = provided_id
        else:
            obj_id = self._next_knowledge_id()
        obj["id"] = obj_id
        path = self.knowledge_dir / f"{obj_id}.json"
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return obj_id

    def load_knowledge(self, obj_id: str) -> Dict[str, Any]:
        if not isinstance(obj_id, str) or not K_PATTERN.match(obj_id):
            raise ValueError("invalid knowledge id format")
        path = self.knowledge_dir / f"{obj_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Knowledge object {obj_id} not found")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_knowledge(self) -> List[str]:
        return sorted([p.stem for p in self.knowledge_dir.glob("*.json") if p.is_file()])

    # Convenience domain-specific save functions
    def save_claim(self, claim: Dict[str, Any]) -> str:
        claim = dict(claim)
        claim.setdefault("type", "claim")
        return self.save_knowledge(claim)

    def save_prediction(self, prediction: Dict[str, Any]) -> str:
        prediction = dict(prediction)
        prediction.setdefault("type", "prediction")
        return self.save_knowledge(prediction)

    def save_experiment(self, experiment: Dict[str, Any]) -> str:
        experiment = dict(experiment)
        experiment.setdefault("type", "experiment")
        return self.save_knowledge(experiment)

    def save_evidence(self, evidence: Dict[str, Any]) -> str:
        evidence = dict(evidence)
        evidence.setdefault("type", "evidence")
        return self.save_knowledge(evidence)

    def save_replication(self, replication: Dict[str, Any]) -> str:
        replication = dict(replication)
        replication.setdefault("type", "replication")
        return self.save_knowledge(replication)

    # ---- events API ----
    def _next_event_id(self) -> str:
        existing = [p.stem for p in self.events_dir.glob("*.json") if p.is_file()]
        nums: List[int] = []
        for name in existing:
            if name.startswith("EV-"):
                try:
                    nums.append(int(name.split("-", 1)[1]))
                except Exception:
                    continue
        next_num = (max(nums) + 1) if nums else 1
        return f"EV-{next_num:04d}"

    def save_event(self, event: Dict[str, Any]) -> str:
        event = dict(event)
        provided_id = event.get("id")
        if provided_id is not None:
            if not isinstance(provided_id, str) or not EV_PATTERN.match(provided_id):
                raise ValueError("event id must match format EV-XXXX (e.g. EV-0001)")
            event_id = provided_id
        else:
            event_id = self._next_event_id()
        event["id"] = event_id
        path = self.events_dir / f"{event_id}.json"
        path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
        return event_id

    def load_event(self, event_id: str) -> Dict[str, Any]:
        if not isinstance(event_id, str) or not EV_PATTERN.match(event_id):
            raise ValueError("invalid event id format")
        path = self.events_dir / f"{event_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Event {event_id} not found")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_events(self) -> List[str]:
        return sorted([p.stem for p in self.events_dir.glob("*.json") if p.is_file()])
