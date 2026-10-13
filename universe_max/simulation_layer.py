"""Simulation layer for Universe-Max.

Runs domain simulations using the ICV runtime. Simulation is a best-effort
orchestration of existing ICV analysis and recommendation logic.
"""
from __future__ import annotations

from typing import Any, Dict


def run_simulation(icv, obj_id: str) -> Dict[str, Any]:
    # delegate to icv.analyze and icv.recommendation
    out: Dict[str, Any] = {}
    try:
        analysis = icv.analyze(obj_id)
        out["analysis"] = analysis
        try:
            out["recommendation"] = icv.recommendation(obj_id)
        except Exception:
            out["recommendation"] = None
    except Exception as e:
        out["error"] = str(e)
    return out
