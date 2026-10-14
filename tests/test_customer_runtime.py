"""Tests for customer runtime."""
from __future__ import annotations

from customer.customer_registry import CustomerRegistry
from customer.engagement_tracker import EngagementTracker
from customer.capability_usage import CapabilityUsage
from runtime.store import MAXLegacyStore


def test_customer_flow(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)

    cr = CustomerRegistry(store)
    et = EngagementTracker(store)
    cu = CapabilityUsage(store)

    cid = cr.register_customer({"name": "Beta"})
    assert cr.get_customer(cid)["name"] == "Beta"

    eid = et.track_engagement(cid, {"event": "trial_start"})
    assert eid.startswith("ENG-")

    uid = cu.record_usage(cid, "CAP-1", {"outcome": "success"})
    assert uid.startswith("U-")
