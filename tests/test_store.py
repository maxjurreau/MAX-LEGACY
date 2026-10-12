import os
from pathlib import Path
from runtime.store import MAXLegacyStore


def test_store_id_generation_and_persistence(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)

    # save first knowledge -> K-001
    kid = store.save_knowledge({"title": "First"})
    assert kid == "K-001"
    assert (root / "knowledge" / "K-001.json").exists()

    # save second knowledge -> K-002
    kid2 = store.save_knowledge({"title": "Second"})
    assert kid2 == "K-002"

    # explicit id must match pattern
    try:
        store.save_knowledge({"id": "BAD", "title": "X"})
        assert False, "invalid id should raise"
    except ValueError:
        pass

    # events sequential
    eid1 = store.save_event({"type": "test", "payload": {}})
    assert eid1 == "EV-0001"
    eid2 = store.save_event({"type": "test", "payload": {}})
    assert eid2 == "EV-0002"

    # explicit event id must match
    try:
        store.save_event({"id": "EV-1", "type": "x", "payload": {}})
        assert False
    except ValueError:
        pass
