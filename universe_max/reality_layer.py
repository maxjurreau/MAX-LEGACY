"""Reality evaluation layer for Universe-MAX.

Evaluates simulation results against knowledge and dependency analysis provided
by QCERuntime. Produces a simple report structure usable by render_view().
"""
from __future__ import annotations

from typing import Any, Dict, List

from runtime.qce import QCERuntime
from .knowledge_layer import KnowledgeManager


class RealityEvaluator:
    def __init__(self, qce: QCERuntime, knowledge: KnowledgeManager) -> None:
        self.qce = qce
        self.knowledge = knowledge

    def evaluate(self, simulation_result: Dict[str, Any]) -> Dict[str, Any]:
        # simple heuristic: collect icv ids and check knowledge coverage
        timeline = simulation_result.get("timeline", [])
        icv_ids = set()
        for step in timeline:
            for out in step.get("outputs", []):
                if "icv" in out:
                    icv_ids.add(out["icv"])
        # check for knowledge objects about these icvs (by id)
        known = []
        unknown = []
        for iid in sorted(icv_ids):
            # knowledge ids in the store are K-###; we treat icv->knowledge mapping naively
            # look through stored knowledge for entries referencing the icv id
            found = []
            for kid in self.knowledge.list_ids():
                obj = self.knowledge.load(kid)
                payload = obj.get("payload") or obj
                if payload.get("icv_id") == iid or payload.get("id") == iid:
                    found.append(kid)
            if found:
                known.extend(found)
            else:
                unknown.append(iid)
        # use QCE to analyze any declared dependencies if available
        try:
            deps = self.qce.load_dependencies()
            impacted = self.qce.analyze_impact(list(known))
        except Exception:
            deps = {}
            impacted = []
        report = {
            "icv_count": len(icv_ids),
            "known_knowledge_ids": known,
            "unknown_icvs": unknown,
            "dependencies": deps,
            "impacted_domains": impacted,
        }
        return report
