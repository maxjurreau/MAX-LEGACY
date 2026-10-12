from __future__ import annotations

from typing import Dict, List, Any
from .district_registry import DistrictRegistry
from runtime.mdt import MDTRuntime


class DistrictViews:
    """Views focused on a specific district (knowledge, history, reality)."""

    def __init__(self, root=None):
        self.registry = DistrictRegistry(root=root)
        self.mdt = MDTRuntime()

    def list_knowledge(self, district_id: str) -> List[Dict[str, Any]]:
        return self.registry.get_district_knowledge(district_id)

    def domain_history(self, district_id: str) -> List[Dict[str, Any]]:
        # Use MDT's domain history as a proxy for district history
        return self.mdt.get_domain_history(district_id)

    def knowledge_objects(self, district_id: str) -> List[Dict[str, Any]]:
        return self.list_knowledge(district_id)


