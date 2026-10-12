"""Pydantic models for the MAX-LEGACY API."""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class KnowledgePayload(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    domain: Optional[str] = None
    entity_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeItem(BaseModel):
    id: str
    domain: Optional[str] = None
    data: Dict[str, Any] | None = None


class PromotionRequest(BaseModel):
    id: str
    domain: Optional[str] = None
    entity_id: Optional[str] = None
    data: Dict[str, Any] | None = None


class EventPayload(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None
