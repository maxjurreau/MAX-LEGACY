"""Identity layer for Universe-MAX.

Provides minimal identity resolution used by the runtime. This is intentionally
lightweight and deterministic to facilitate tests and phased integration with
SIM-UNIVERSITY identity services.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class IdentityManager:
    """Simple in-memory identity manager and resolver."""

    def __init__(self) -> None:
        # maps external identifiers to canonical ids
        self._districts: Dict[str, Dict[str, Any]] = {}
        self._icvs: Dict[str, Dict[str, Any]] = {}

    def register_district(self, district: Dict[str, Any]) -> str:
        did = district.get("id")
        if not did:
            raise ValueError("district must include id")
        self._districts[did] = district
        return did

    def resolve_district(self, did: str) -> Optional[Dict[str, Any]]:
        return self._districts.get(did)

    def register_icv(self, icv: Dict[str, Any]) -> str:
        iid = icv.get("id")
        if not iid:
            raise ValueError("icv must include id")
        self._icvs[iid] = icv
        return iid

    def resolve_icv(self, iid: str) -> Optional[Dict[str, Any]]:
        return self._icvs.get(iid)
