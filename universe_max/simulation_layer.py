from __future__ import annotations

from typing import Dict, Any, Optional
from runtime.event_engine import EventEngine
from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime


class SimulationLayer:
    """Run lightweight deterministic simulations that emit events through EventEngine.

    Simulations are not autonomous agents; they are deterministic runners that
    use the existing EventEngine and MDT for persistence and tracking.
    """

    def __init__(self, root: Optional[str] = None):
        self.store = MAXLegacyStore(root=root)
        self.engine = EventEngine(store=self.store)
        self.mdt = MDTRuntime()

    def run_simulation(self, sim_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # produce a synthetic event and record it via MDT
        payload = {"sim_id": sim_id, "inputs": inputs}
        ev = self.engine.emit_event("simulation", payload)
        self.mdt.record_event(ev)
        return ev
