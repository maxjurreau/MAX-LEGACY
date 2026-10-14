"""Tests for identity layer."""
from __future__ import annotations

from universe_max.identity_layer import IdentityManager


def test_identity_register_resolve():
    im = IdentityManager()
    d = {"id": "D1", "name": "District"}
    im.register_district(d)
    assert im.resolve_district("D1") == d
    icv = {"id": "I1", "name": "icv"}
    im.register_icv(icv)
    assert im.resolve_icv("I1") == icv
