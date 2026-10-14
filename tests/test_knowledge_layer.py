"""Tests for knowledge layer."""
from __future__ import annotations

from runtime.store import MAXLegacyStore
from universe_max.knowledge_layer import KnowledgeManager


def test_knowledge_save_load(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)
    km = KnowledgeManager(store)
    kid = km.save({"type": "claim", "payload": {"foo": "bar"}})
    assert kid.startswith("K-")
    obj = km.load(kid)
    assert obj["payload"]["foo"] == "bar"
    ids = km.list_ids()
    assert kid in ids
