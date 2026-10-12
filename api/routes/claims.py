from __future__ import annotations

from fastapi import APIRouter

from api.dependencies import get_event_engine, get_mdt, get_qce, get_store
from api.models import KnowledgeItem
from runtime.exceptions import ValidationError

router = APIRouter()


def validate_knowledge(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValidationError("knowledge data must be an object")
    if "title" not in data and "name" not in data:
        raise ValidationError("knowledge object must contain title or name")


def validate_promotion(item: dict) -> None:
    if not isinstance(item, dict):
        raise ValidationError("promotion must be an object")
    if "entity_id" not in item and (item.get("data") or {}).get("id") is None:
        raise ValidationError("promotion must reference entity_id or data.id")
    if not item.get("domain"):
        raise ValidationError("promotion must include target domain")


@router.post("/claims")
async def create_claim(item: KnowledgeItem):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.model_dump())
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    store = get_store()
    engine = get_event_engine()
    mdt = get_mdt()
    qce = get_qce()

    try:
        store.save_claim({"id": item.id, "domain": item.domain, **(item.data or {})})
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    try:
        ev = engine.emit_event("claim", {"id": item.id, "domain": item.domain, **(item.data or {})})
        mdt.record_event(ev)
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    affected = qce.analyze_impact([item.domain or "Claims"]) if qce._deps else []
    return {"status": "success", "event_id": ev.get("id"), "affected_domains": affected}


@router.post("/predictions")
async def create_prediction(item: KnowledgeItem):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.model_dump())
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    store = get_store()
    engine = get_event_engine()
    mdt = get_mdt()
    try:
        store.save_prediction({"id": item.id, "domain": item.domain, **(item.data or {})})
        ev = engine.emit_event("prediction", {"id": item.id, "domain": item.domain, **(item.data or {})})
        mdt.record_event(ev)
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}
    return {"status": "success", "event_id": ev.get("id")}


@router.post("/experiments")
async def create_experiment(item: KnowledgeItem):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.model_dump())
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    store = get_store(); engine = get_event_engine(); mdt = get_mdt()
    try:
        store.save_experiment({"id": item.id, "domain": item.domain, **(item.data or {})})
        ev = engine.emit_event("experiment", {"id": item.id, "domain": item.domain, **(item.data or {})})
        mdt.record_event(ev)
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}
    return {"status": "success", "event_id": ev.get("id")}


@router.post("/evidence")
async def create_evidence(item: KnowledgeItem):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.model_dump())
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    store = get_store(); engine = get_event_engine(); mdt = get_mdt()
    try:
        store.save_evidence({"id": item.id, "domain": item.domain, **(item.data or {})})
        ev = engine.emit_event("evidence", {"id": item.id, "domain": item.domain, **(item.data or {})})
        mdt.record_event(ev)
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}
    return {"status": "success", "event_id": ev.get("id")}


@router.post("/replications")
async def create_replication(item: KnowledgeItem):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.model_dump())
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    store = get_store(); engine = get_event_engine(); mdt = get_mdt()
    try:
        store.save_replication({"id": item.id, "domain": item.domain, **(item.data or {})})
        ev = engine.emit_event("replication", {"id": item.id, "domain": item.domain, **(item.data or {})})
        mdt.record_event(ev)
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}
    return {"status": "success", "event_id": ev.get("id")}


@router.post("/knowledge")
async def create_knowledge(item: KnowledgeItem):
    try:
        validate_knowledge(item.data or {})
        validate_promotion(item.model_dump())
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}

    store = get_store(); engine = get_event_engine(); mdt = get_mdt()
    try:
        store.save_knowledge({"id": item.id, "domain": item.domain, **(item.data or {})})
        ev = engine.emit_event("knowledge", {"id": item.id, "domain": item.domain, **(item.data or {})})
        mdt.record_event(ev)
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}
    return {"status": "success", "event_id": ev.get("id")}


@router.get("/knowledge/{id}")
async def get_knowledge_by_id(id: str):
    try:
        return get_store().load_knowledge(id)
    except Exception as exc:
        return {"detail": str(exc)}


@router.get("/events/{id}")
async def get_event_by_id(id: str):
    try:
        return get_store().load_event(id)
    except Exception as exc:
        return {"detail": str(exc)}


@router.get("/domains")
async def list_domains():
    qce = get_qce()
    return {"domains": sorted(list(qce._deps.keys()))}


@router.get("/health")
async def health():
    return {"status": "ok"}


router_for_main = router
