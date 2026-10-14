"""Universe MAX core runtime orchestration.

Provides UniverseRuntime which composes identity, knowledge, simulation,
reality and rendering layers and exposes the required public methods.
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime
from runtime.event_engine import EventEngine

from .identity_layer import IdentityManager
from .knowledge_layer import KnowledgeManager
from .simulation_layer import SimulationEngine
from .reality_layer import RealityEvaluator
from .render_layer import render_view as render_fn


class UniverseRuntime:
    """Shared operating environment for Universe-MAX.

    Responsibilities implemented:
    - Shared runtime context
    - Knowledge access
    - District access
    - ICV access
    - Simulation execution
    - Reality evaluation
    - Context persistence
    """

    def __init__(
        self,
        store: Optional[MAXLegacyStore] = None,
        mdt: Optional[MDTRuntime] = None,
        qce: Optional[QCERuntime] = None,
        event_engine: Optional[EventEngine] = None,
    ) -> None:
        # initialize backing components (use defaults if not provided)
        self.store = store or MAXLegacyStore()
        self.mdt = mdt or MDTRuntime(storage_path=os.path.join("runtime", "_mdt_store.json"))
        self.qce = qce or QCERuntime()
        self.event_engine = event_engine or EventEngine(store=self.store)

        # managers
        self.identity = IdentityManager()
        self.knowledge = KnowledgeManager(self.store)
        self.simulation = SimulationEngine()
        self.reality = RealityEvaluator(self.qce, self.knowledge)

        # runtime context
        self.context: Dict[str, Any] = {
            "districts": {},
            "icvs": {},
            "last_simulation": None,
            "metadata": {},
        }

    # ---- loader APIs ----
    def load_district(self, district: Dict[str, Any]) -> str:
        """Load a research district into runtime context and record it with MDT."""
        did = district.get("id") or f"DIST-{uuid.uuid4().hex[:8]}"
        district = dict(district)
        district["id"] = did
        self.context["districts"][did] = district
        # record a domain update in MDT
        self.mdt.record_domain_update({"domain": "district", "id": did, "district": district})
        return did

    def load_icv(self, icv: Dict[str, Any]) -> str:
        """Load an ICV into runtime. ICV is a dict describing a simulated agent or a module spec."""
        iid = icv.get("id") or f"ICV-{uuid.uuid4().hex[:8]}"
        icv = dict(icv)
        icv["id"] = iid
        self.context["icvs"][iid] = icv
        # register in MDT timeline
        self.mdt.record_change({"entity_id": iid, "domain": "icv", "change": "loaded"})
        return iid

    def load_knowledge(self, obj: Dict[str, Any]) -> str:
        """Persist knowledge via the store and return its id."""
        kid = self.knowledge.save(obj)
        # record event via MDT
        self.mdt.record_event({"id": f"EV-{uuid.uuid4().hex[:8]}", "type": "knowledge_loaded", "payload": {"id": kid}})
        return kid

    # ---- persistence APIs ----
    def save_context(self, name: Optional[str] = None) -> str:
        """Serialize runtime context and save to runtime/universe_contexts/<name>.json."""
        base = Path(self.store.root)
        out_dir = base / "universe_contexts"
        out_dir.mkdir(parents=True, exist_ok=True)
        if name is None:
            name = f"context-{uuid.uuid4().hex[:8]}.json"
        path = out_dir / name
        data = {
            "context": self.context,
            "metadata": self.context.get("metadata", {}),
            "last_simulation": self.context.get("last_simulation"),
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def restore_context(self, path_or_data: Any) -> None:
        """Restore context from a file path or dict produced by save_context."""
        if isinstance(path_or_data, (str, Path)):
            p = Path(path_or_data)
            if not p.exists():
                raise FileNotFoundError(str(p))
            data = json.loads(p.read_text(encoding="utf-8"))
        elif isinstance(path_or_data, dict):
            data = path_or_data
        else:
            raise ValueError("path_or_data must be a path or a dict")
        ctx = data.get("context") or {}
        self.context.update(ctx)
        # restore last_simulation into simulation manager if present
        if self.context.get("last_simulation"):
            self.simulation.last_result = self.context["last_simulation"]

    # ---- runtime execution ----
    def run_simulation(self, district_id: str, icv_ids: Optional[List[str]] = None, steps: int = 1) -> Dict[str, Any]:
        district = self.context["districts"].get(district_id)
        if district is None:
            raise KeyError(f"district {district_id} not loaded")
        if icv_ids is None:
            icv_ids = list(self.context["icvs"].keys())
        icvs = [self.context["icvs"][i] for i in icv_ids]
        result = self.simulation.run(district, icvs, steps=steps)
        self.context["last_simulation"] = result
        # emit an event
        ev = self.event_engine.emit_event("simulation_run", {"district": district_id, "icvs": icv_ids, "result_summary": result.get("summary")})
        # record in MDT
        self.mdt.record_event(ev)
        return result

    def evaluate_reality(self, simulation_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if simulation_result is None:
            simulation_result = self.context.get("last_simulation")
            if simulation_result is None:
                raise ValueError("no simulation result to evaluate")
        report = self.reality.evaluate(simulation_result)
        # emit an evaluation event
        ev = self.event_engine.emit_event("reality_evaluation", {"report": report})
        self.mdt.record_event(ev)
        return report

    def render_view(self, simulation_result: Optional[Dict[str, Any]] = None, evaluation: Optional[Dict[str, Any]] = None) -> str:
        if simulation_result is None:
            simulation_result = self.context.get("last_simulation")
        return render_fn(self.context, simulation_result, evaluation)
