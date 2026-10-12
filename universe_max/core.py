from __future__ import annotations

from typing import Any, Dict, Optional

from .identity_layer import IdentityLayer
from .simulation_layer import SimulationLayer
from .knowledge_layer import KnowledgeLayer
from .reality_layer import RealityLayer
from .render_layer import RenderLayer


class UniverseCore:
    """Shared operating environment that composes layers and exposes simple API."""

    def __init__(self, root: Optional[str] = None):
        self.identity = IdentityLayer(root=root)
        self.simulation = SimulationLayer(root=root)
        self.knowledge = KnowledgeLayer(root=root)
        self.reality = RealityLayer(root=root)
        self.render = RenderLayer(root=root)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "identities": self.identity.count_identities(),
            "knowledge_objects": len(self.knowledge.list_objects()),
        }
