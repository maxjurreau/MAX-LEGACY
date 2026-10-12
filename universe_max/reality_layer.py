from __future__ import annotations

from runtime.reality_views import RealityViews


class RealityLayer:
    """Facade over RealityViews and MAX-REALITY artifacts."""

    def __init__(self, root: Optional[str] = None):
        self.reality = RealityViews(root=root)

    def object_alignment(self, obj_id: str):
        return self.reality.object_alignment(obj_id)

    def district_alignment(self, district_id: str):
        return self.reality.district_alignment(district_id)
