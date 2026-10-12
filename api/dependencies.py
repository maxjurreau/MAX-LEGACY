"""Shared FastAPI dependencies for MAX-LEGACY runtime objects."""
from __future__ import annotations

from functools import lru_cache

from runtime.event_engine import EventEngine
from runtime.mdt import MDTRuntime
from runtime.qce import QCERuntime
from runtime.store import MAXLegacyStore


@lru_cache(maxsize=1)
def get_store() -> MAXLegacyStore:
    return MAXLegacyStore()


@lru_cache(maxsize=1)
def get_event_engine() -> EventEngine:
    return EventEngine(store=get_store())


@lru_cache(maxsize=1)
def get_mdt() -> MDTRuntime:
    return MDTRuntime()


@lru_cache(maxsize=1)
def get_qce() -> QCERuntime:
    qce = QCERuntime()
    try:
        qce.load_dependencies()
    except Exception:
        pass
    return qce
