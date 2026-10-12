import os
from runtime.mdt import MDTRuntime


def test_mdt_record_and_retrieve():
    storage = os.path.join("runtime", "test_mdt_store.json")
    try:
        os.remove(storage)
    except FileNotFoundError:
        pass

    mdt = MDTRuntime(storage_path=storage)

    ev = {"type": "test.event", "data": {"id": "E1"}, "domain": "Tests", "entity_id": "E1"}
    ev_id = mdt.record_event(ev)
    assert ev_id is not None
    timeline = mdt.get_timeline("E1")
    assert any(item["type"] == "event" and item["id"] == ev_id for item in timeline)
    domain_history = mdt.get_domain_history("Tests")
    assert any(e["id"] == ev_id or e.get("id") == ev_id for e in domain_history)
