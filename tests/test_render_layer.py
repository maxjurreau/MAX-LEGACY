"""Tests for render layer."""
from __future__ import annotations

from universe_max.render_layer import render_view


def test_render_view_output():
    ctx = {"districts": {"D1": {}}, "icvs": {"I1": {}}, "last_simulation": None}
    sim = {"summary": {"steps": 1, "icv_count": 1}}
    eval_ = {"known_knowledge_ids": [], "unknown_icvs": []}
    out = render_view(ctx, sim, eval_)
    assert "Universe-MAX Runtime View" in out
