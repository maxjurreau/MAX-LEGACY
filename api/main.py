from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict

from runtime.store import MAXLegacyStore
from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime

app = FastAPI(title="MAX-LEGACY Runtime v1.0")

store = MAXLegacyStore()
engine = EventEngine(store=store)
mdt = MDTRuntime()
qce = QCERuntime()
try:
    qce.load_dependencies()
except Exception:
    # if dependency loading fails, continue but QCE analysis will return empty
    pass


class Item(BaseModel):
    id: str
    domain: str | None = None
    data: Dict[str, Any] | None = None


def validate_knowledge(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("knowledge data must be an object")
    if "title" not in data and "name" not in data:
        raise ValueError("knowledge object must contain title or name")


def validate_promotion(item: Dict[str, Any]) -> None:
    # Minimal promotion validation: must reference an entity and have a target domain
    if not isinstance(item, dict):
        raise ValueError("promotion must be an object")
    if "entity_id" not in item and (item.get("data") or {}).get("id") is None:
        raise ValueError("promotion must reference entity_id or data.id")
    if not item.get("domain"):
        raise ValueError("promotion must include target domain")


def _fail(detail: str):
    return JSONResponse(status_code=400, content={"status": "FAIL", "reason": detail})


@app.post("/claims")
async def post_claim(item: Item):
    # run validation
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.dict())
    except Exception as e:
        return _fail(str(e))

    # create knowledge object in store
    try:
        store.save_claim({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    # emit event via engine
    try:
        ev = engine.emit_event("claim", {"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    # record in MDT
    try:
        mdt.record_event(ev)
    except Exception:
        # MDT failures should not leave API hanging; return failure
        return _fail("mdt record failed")

    # run QCE analysis on domain
    affected = qce.analyze_impact([item.domain or "Claims"]) if qce._deps else []
    return {"status": "success", "event_id": ev.get("id"), "affected_domains": affected}


@app.post("/predictions")
async def post_prediction(item: Item):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.dict())
    except Exception as e:
        return _fail(str(e))

    try:
        store.save_prediction({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    try:
        ev = engine.emit_event("prediction", {"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    mdt.record_event(ev)
    return {"status": "success", "event_id": ev.get("id")}


@app.post("/experiments")
async def post_experiment(item: Item):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.dict())
    except Exception as e:
        return _fail(str(e))

    try:
        store.save_experiment({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    try:
        ev = engine.emit_event("experiment", {"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    mdt.record_event(ev)
    return {"status": "success", "event_id": ev.get("id")}


@app.post("/evidence")
async def post_evidence(item: Item):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.dict())
    except Exception as e:
        return _fail(str(e))

    try:
        store.save_evidence({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    try:
        ev = engine.emit_event("evidence", {"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    mdt.record_event(ev)
    return {"status": "success", "event_id": ev.get("id")}


@app.post("/replications")
async def post_replication(item: Item):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.dict())
    except Exception as e:
        return _fail(str(e))

    try:
        store.save_replication({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    try:
        ev = engine.emit_event("replication", {"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    mdt.record_event(ev)
    return {"status": "success", "event_id": ev.get("id")}


@app.post("/knowledge")
async def post_knowledge(item: Item):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.dict())
    except Exception as e:
        return _fail(str(e))

    try:
        store.save_knowledge({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    try:
        ev = engine.emit_event("knowledge", {"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as e:
        return _fail(str(e))

    mdt.record_event(ev)
    return {"status": "success", "event_id": ev.get("id")}


@app.get("/knowledge/{id}")
async def get_knowledge(id: str):
    try:
        obj = store.load_knowledge(id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return obj


@app.get("/events/{id}")
async def get_event(id: str):
    try:
        ev = store.load_event(id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ev


@app.get("/domains")
async def get_domains():
    return {"domains": sorted(list(qce._deps.keys()))}


@app.get("/health")
async def health():
    return {"status": "ok"}
