from pathlib import Path
from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine


def test_event_engine_validation_and_sequential_ids(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    store = MAXLegacyStore(root=root)
    engine = EventEngine(store=store)

    # missing required field should be rejected
    try:
        engine.emit_event("test", {"id": "X"})
        assert False, "missing payload should raise"
    except ValueError:
        pass

    # valid event should be created and have sequential EV ids
    ev1 = engine.emit_event("test", {"id": "A", "domain": "T"})
    ev2 = engine.emit_event("test", {"id": "B", "domain": "T"})
    ev3 = engine.emit_event("test", {"id": "C", "domain": "T"})

    assert ev1.get("id") == "EV-0001"
    assert ev2.get("id") == "EV-0002"
    assert ev3.get("id") == "EV-0003"
