"""Simulation layer for Universe-MAX.

Implements a deterministic, testable SimulationEngine that runs simple ICV
behaviors over a number of steps and returns structured results.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SimulationEngine:
    def __init__(self) -> None:
        self.last_result: Optional[Dict[str, Any]] = None

    def _run_icv_step(self, icv: Dict[str, Any], step: int) -> Dict[str, Any]:
        # icv may contain a 'behavior' callable or a simple spec
        behavior = icv.get("behavior")
        if callable(behavior):
            out = behavior(icv, step)
        else:
            # deterministic fallback: echo icv id and step
            out = {"icv": icv.get("id"), "step": step, "value": icv.get("value", 1) * (step + 1)}
        return out

    def run(self, district: Dict[str, Any], icvs: List[Dict[str, Any]], steps: int = 1) -> Dict[str, Any]:
        timeline: List[Dict[str, Any]] = []
        for s in range(steps):
            step_out: List[Dict[str, Any]] = []
            for icv in icvs:
                step_out.append(self._run_icv_step(icv, s))
            timeline.append({"step": s, "outputs": step_out})
        summary = {"district": district.get("id"), "steps": steps, "icv_count": len(icvs)}
        result = {"timeline": timeline, "summary": summary}
        self.last_result = result
        return result
