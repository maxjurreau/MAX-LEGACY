"""Tests for umbrella runtime."""
from __future__ import annotations

from pathlib import Path

from umbrella.umbrella_runtime import UmbrellaRuntime
from runtime.store import MAXLegacyStore


def test_umbrella_basic_flow(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)
    ur = UmbrellaRuntime(store=store)

    # create customer
    cid = ur.create_customer({"name": "ACME"})
    assert cid

    # create project
    pid = ur.create_project({"name": "Project X"})
    assert pid

    # assign a capability
    capid = ur.assign_capability(pid, {"name": "Forecasting", "base_price": 100.0})
    caps = ur.list_capabilities()
    assert any(c.get("id") == capid for c in caps)

    # record revenue
    rid = ur.record_revenue({"amount": 150.0, "customer": cid, "project": pid})
    assert rid

    # generate report
    rep = ur.generate_report()
    assert rep["customers"] == 1
    assert rep["projects"] == 1
    assert rep["capabilities"] >= 1
    assert rep["revenue"] >= 150.0
