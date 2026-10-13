"""Tests for the Universe-Max runtime.

These tests verify the minimal runtime flow using an in-memory fake store and
a fake ICV implementation. The tests avoid touching external services and
exercise the public UniverseMax APIs.
"""
from __future__ import annotations

import pytest

from universe_max.core import UniverseMax


class FakeStore:
    def __init__(self):
        self._knowledge = {
            "k1": {"id": "k1", "title": "Test Knowledge", "domain": "research", "alignment": {"score": 0.8}, "body": "sample"}
        }
        self._contexts = {}

    def load_knowledge(self, obj_id: str):
        return self._knowledge.get(obj_id)

    def list_knowledge(self):
        return list(self._knowledge.keys())

    def save_context(self, key: str, value):
        self._contexts[key] = value

    def load_context(self, key: str):
        return self._contexts.get(key)


class FakeICV:
    def __init__(self, store=None):
        self._store = store

    def analyze(self, obj_id: str):
        obj = self._store.load_knowledge(obj_id)
        return {"id": obj_id, "score": 0.75, "meta": {"title": obj.get("title")}} if obj else None

    def alignment(self, obj_id: str):
        obj = self._store.load_knowledge(obj_id)
        return obj.get("alignment") if obj else None

    def knowledge(self, obj_id: str):
        return self._store.load_knowledge(obj_id)

    def recommendation(self, obj_id: str):
        return {"id": obj_id, "action": "promote"}


class DummyManager:
    def __init__(self, store):
        self.store = store

    def instantiate(self, name: str):
        return FakeICV(store=self.store)


def test_universe_runtime_flow():
    store = FakeStore()
    um = UniverseMax(store=store, icv_manager=DummyManager(store))

    # load knowledge
    k = um.load_knowledge("k1")
    assert k and k.get("title") == "Test Knowledge"

    # load icv and run simulation
    icv = um.load_icv("research")
    sim = um.run_simulation(icv, "k1")
    assert "simulation" in sim and sim["simulation"].get("score") == 0.75

    # evaluate reality
    reality = um.evaluate_reality(icv, "k1")
    assert "reality_evaluation" in reality
    assert reality["reality_evaluation"]["alignment_score"] == 0.8

    # render view
    view = um.render_view(icv, "k1")
    assert "view" in view and view["view"].get("title") == "Test Knowledge"

    # context save/restore
    assert um.save_context("x", {"v": 1}) is True
    assert um.restore_context("x") == {"v": 1}
