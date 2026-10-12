import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict

from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime

app = FastAPI(title="MAX-LEGACY Runtime v1.0")

mdt = MDTRuntime()
qce = QCERuntime()
qce.load_dependencies()


class Item(BaseModel):
    id: str
    domain: str | None = None
    data: Dict[str, Any] | None = None


def validate_knowledge_object(data: Dict[str, Any]) -> None:
    # basic semantic validation for knowledge objects
    if not isinstance(data, dict):
        raise ValueError("knowledge data must be an object")
    if "title" not in data and "name" not in data:
        raise ValueError("knowledge object missing title/name")


@app.post("/claims")
async def post_claim(item: Item):
    if not item.id:
        raise HTTPException(status_code=400, detail="id required")

    # If this is the canonical K-001, emit EV-0001
    event = {"type": "claim", "data": item.data or {}, "domain": item.domain or "Claims", "entity_id": item.id}
    if item.id == "K-001":
        event["id"] = "EV-0001"

    # validate event
    try:
        mdt._validate_event(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    ev_id = mdt.record_event(event)

    # integrate QCE into promotion flow: analyze impact of the domain
    affected = qce.analyze_impact([event.get("domain")])

    return JSONResponse({"status": "success", "event_id": ev_id, "affected_domains": sorted(set(affected))})


@app.post("/predictions")
async def post_prediction(item: Item):
    event = {"type": "prediction", "data": item.data or {}, "domain": item.domain or "Predictions", "entity_id": item.id}
    try:
        mdt._validate_event(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    ev_id = mdt.record_event(event)
    return {"status": "success", "event_id": ev_id}


@app.post("/experiments")
async def post_experiment(item: Item):
    event = {"type": "experiment", "data": item.data or {}, "domain": item.domain or "Experiments", "entity_id": item.id}
    mdt._validate_event(event)
    ev_id = mdt.record_event(event)
    return {"status": "success", "event_id": ev_id}


@app.post("/evidence")
async def post_evidence(item: Item):
    event = {"type": "evidence", "data": item.data or {}, "domain": item.domain or "Evidence", "entity_id": item.id}
    try:
        mdt._validate_event(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # knowledge validation when evidence contains knowledge
    if event.get("type") == "evidence" and isinstance(event.get("data"), dict):
        try:
            validate_knowledge_object(event.get("data"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    ev_id = mdt.record_event(event)
    return {"status": "success", "event_id": ev_id}


@app.post("/replications")
async def post_replication(item: Item):
    event = {"type": "replication", "data": item.data or {}, "domain": item.domain or "Replications", "entity_id": item.id}
    mdt._validate_event(event)
    ev_id = mdt.record_event(event)
    return {"status": "success", "event_id": ev_id}


@app.post("/knowledge")
async def post_knowledge(item: Item):
    try:
        validate_knowledge_object(item.data or {})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    event = {"type": "knowledge", "data": item.data or {}, "domain": item.domain or "Knowledge", "entity_id": item.id}
    ev_id = mdt.record_event(event)
    return {"status": "success", "event_id": ev_id}


@app.get("/knowledge/{id}")
async def get_knowledge(id: str):
    history = mdt.get_entity_history(id)
    if not history:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": id, "history": history}


@app.get("/events/{id}")
async def get_event(id: str):
    for e in mdt._data.get("events", []):
        if e.get("id") == id:
            return e
    raise HTTPException(status_code=404, detail="not found")


@app.get("/domains")
async def get_domains():
    return {"domains": sorted(list(qce._deps.keys()))}


@app.get("/health")
async def health():
    return {"status": "ok"}
