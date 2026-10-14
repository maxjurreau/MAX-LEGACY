"""Tests for Universe-MAX runtime foundation."""
from __future__ import annotations

import json
from pathlib import Path

from universe_max.core import UniverseRuntime
from runtime.store import MAXLegacyStore
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime
from runtime.event_engine import EventEngine


def test_universe_runtime_end_to_end(tmp_path):
    # prepare a filesystem-backed store rooted at tmp_path
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    store = MAXLegacyStore(root=repo_root)
    mdt = MDTRuntime(storage_path=str(repo_root / "runtime" / "_mdt_store.json"))
    qce = QCERuntime(path=str(repo_root / "schema" / "dependencies.yaml"))
    event_engine = EventEngine(store=store)

    ur = UniverseRuntime(store=store, mdt=mdt, qce=qce, event_engine=event_engine)

    # Load a district
    district = {"name": "Research District Alpha"}
    did = ur.load_district(district)
    assert did in ur.context["districts"]

    # Load an ICV
    icv = {"name": "Test ICV", "value": 2}
    iid = ur.load_icv(icv)
    assert iid in ur.context["icvs"]

    # Load knowledge about the icv
    kobj = {"type": "evidence", "payload": {"icv_id": iid, "note": "seed evidence"}}
    kid = ur.load_knowledge(kobj)
    assert kid.startswith("K-")

    # Run simulation
    sim = ur.run_simulation(did, [iid], steps=2)
    assert sim["summary"]["steps"] == 2

    # Evaluate reality
    report = ur.evaluate_reality(sim)
    assert isinstance(report, dict)
    assert report["icv_count"] == 1

    # Render view
    view = ur.render_view(simulation_result=sim, evaluation=report)
    assert "Universe-MAX Runtime View" in view

    # Save and restore context
    p = ur.save_context()
    assert Path(p).exists()
    ur2 = UniverseRuntime(store=store, mdt=mdt, qce=qce, event_engine=event_engine)
    ur2.restore_context(p)
    assert ur2.context.get("last_simulation") is not None
