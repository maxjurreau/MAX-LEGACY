from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json

from runtime.store import MAXLegacyStore
from runtime.config import DEFAULT_CONFIG
from runtime.audit import DEFAULT_AUDIT_TRAIL
from runtime.exceptions import DomainNotFoundError


class DistrictRegistry:
    """Registry for districts built on top of existing knowledge objects.

    This module provides safe, read-only access to district groupings derived
    from knowledge objects stored by MAXLegacyStore. It intentionally does not
    introduce new districts or modify stored objects; it merely indexes them.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        repo_root = Path(root) if root is not None else DEFAULT_CONFIG.repo_root
        self.store = MAXLegacyStore(root=repo_root)
        self.knowledge_dir = self.store.knowledge_dir

    def list_districts(self) -> List[str]:
        """Return sorted list of known district ids."""
        districts = set()
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                d = obj.get("district")
                if d:
                    districts.add(str(d))
            except Exception:
                # ignore unreadable or malformed files
                continue
        DEFAULT_AUDIT_TRAIL.record("list_districts", {"count": len(districts)})
        return sorted(districts)

    def get_district_knowledge(self, district_id: str) -> List[Dict]:
        """Return knowledge objects belonging to a district."""
        if not district_id:
            raise DomainNotFoundError("empty district id")
        results: List[Dict] = []
        for p in self.knowledge_dir.glob("*.json"):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                if obj.get("district") == district_id:
                    results.append(obj)
            except Exception:
                continue
        DEFAULT_AUDIT_TRAIL.record("get_district_knowledge", {"district": district_id, "count": len(results)})
        return results

    # Alias kept for compatibility
    def list_district_ids(self) -> List[str]:
        return self.list_districts()


