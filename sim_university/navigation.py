from __future__ import annotations

from typing import Dict, List, Any
from pathlib import Path
import json

from .district_registry import DistrictRegistry
from .icv_registry import ICVRegistry


class Navigation:
    """Generate navigable views based on districts and ICVs.

    Produces lightweight structures that can be rendered by UI layers.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
        self.districts = DistrictRegistry(root=self.root)
        self.icvs = ICVRegistry(root=self.root)

    def district_index(self) -> List[Dict[str, Any]]:
        """Return an index of districts and counts of objects and ICVs."""
        result = []
        for d in self.districts.list_districts():
            objs = self.districts.get_district_knowledge(d)
            icv_set = set()
            for o in objs:
                icv = o.get("icv")
                if isinstance(icv, str):
                    icv_set.add(icv)
                elif isinstance(icv, dict) and icv.get("id"):
                    icv_set.add(icv.get("id"))
            result.append({"district": d, "objects": len(objs), "icvs": sorted(icv_set)})
        return sorted(result, key=lambda x: x["district"])

    def icv_index(self) -> List[Dict[str, Any]]:
        result = []
        for i in self.icvs.list_icvs():
            objs = self.icvs.list_icv_objects(i)
            districts = sorted({o.get("district") for o in objs if o.get("district")})
            result.append({"icv": i, "objects": len(objs), "districts": districts})
        return sorted(result, key=lambda x: x["icv"])

    def navigable_tree(self) -> Dict[str, Any]:
        """Return a nested structure: districts -> objects (with minimal metadata)."""
        tree: Dict[str, Any] = {"districts": []}
        for d in self.districts.list_districts():
            objs = []
            for o in self.districts.get_district_knowledge(d):
                objs.append({"id": o.get("id"), "title": o.get("title") or o.get("name"), "icv": o.get("icv")})
            tree["districts"].append({"district": d, "objects": objs})
        return tree


