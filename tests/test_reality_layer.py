"""Tests for reality layer."""
from __future__ import annotations

from runtime.qce import QCERuntime
from runtime.store import MAXLegacyStore
from universe_max.knowledge_layer import KnowledgeManager
from universe_max.reality_layer import RealityEvaluator


def test_reality_evaluator(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)
    km = KnowledgeManager(store)
    # save a knowledge object referencing I1
    kid = km.save({"type": "evidence", "payload": {"icv_id": "I1"}})
    qce = QCERuntime()
    re = RealityEvaluator(qce, km)
    sim = {"timeline": [{"step": 0, "outputs": [{"icv": "I1", "value": 1}]}]}
    report = re.evaluate(sim)
    assert report["icv_count"] == 1
    assert kid in report["known_knowledge_ids"]
