from runtime.mdt import MDTRuntime


def test_mdt_basic(tmp_path):
    storage = tmp_path / "_mdt_store.json"
    m = MDTRuntime(storage_path=str(storage))

    ev = {"id": "EV-0001", "type": "claim", "payload": {"id": "K-001"}, "domain": "Claims"}
    # record event
    eid = m.record_event(ev)
    assert eid == "EV-0001"
    # timeline
    tl = m.get_timeline("K-001")
    assert any(x["id"] == "EV-0001" for x in tl)
