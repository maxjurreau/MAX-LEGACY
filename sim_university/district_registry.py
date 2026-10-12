from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json

from runtime.store import MAXLegacyStore


class DistrictRegistry:
    """Registry for districts built on top of existing knowledge objects.

    Assumptions:
    - Knowledge objects may include a "district" field identifying their district.
    - District ids are strings. If absent, object is considered undistricted.

    This registry does not introduce new architecture; it uses the existing
    knowledge store (knowledge/*.json) as the source of truth.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        if root is None:
            root = Path(__file__).resolve().parents[1]
        self.root = Path(root)
        self.store = MAXLegacyStore(root=self.root)
        self.knowledge_dir = self.store.knowledge_dir

    def list_districts(self) -> List[str]:
        """Return sorted list of known district ids."""
        districts = set()
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                d = obj.get("district")
                if d:
                    districts.add(d)
            except Exception:
                continue
        return sorted(districts)

    def get_district_knowledge(self, district_id: str) -> List[Dict]:
        """Return knowledge objects belonging to a district."""
        results = []
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                if obj.get("district") == district_id:
                    results.append(obj)
            except Exception:
                continue
        return results

    def list_district_ids(self) -> List[str]:
        # alias
        return self.list_districts()


