"""Tests for revenue runtime."""
from __future__ import annotations

from revenue.revenue_tracker import RevenueTracker, InvoiceEngine
from revenue.subscription_registry import SubscriptionRegistry
from runtime.store import MAXLegacyStore


def test_revenue_flow(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)

    rt = RevenueTracker(store)
    ie = InvoiceEngine(store)
    sr = SubscriptionRegistry(store)

    rid = rt.record_revenue({"amount": 200.0, "source": "capability"})
    assert rid.startswith("REV-")

    inv = ie.create_invoice("C-123", [{"desc": "cap", "amount": 200.0}])
    assert inv.startswith("INV-")

    sid = sr.register_subscription("C-123", {"plan": "pro"})
    assert sid.startswith("S-")
