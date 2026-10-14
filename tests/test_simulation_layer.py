"""Tests for simulation layer."""
from __future__ import annotations

from universe_max.simulation_layer import SimulationEngine


def test_simulation_runs():
    se = SimulationEngine()
    district = {"id": "D1"}
    icvs = [{"id": "I1", "value": 3}, {"id": "I2", "value": 5}]
    res = se.run(district, icvs, steps=3)
    assert res["summary"]["steps"] == 3
    assert res["summary"]["icv_count"] == 2
    assert len(res["timeline"]) == 3
