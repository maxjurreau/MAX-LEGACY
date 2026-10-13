"""ICV base class and contract.

Every ICV must implement the following methods:
- identity()
- knowledge()
- history()
- alignment()
- recommendation()
- related_domains()
- related_knowledge()
- related_evidence()
- status()

This module provides an abstract BaseICV that concrete ICVs should subclass.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class Identity:
    id: Optional[str]
    name: Optional[str]


class BaseICV(ABC):
    """Abstract base for ICVs (Information/Intelligence/Insight Context Vectors).

    Subclasses MUST implement all abstract methods in the contract.
    """

    def __init__(self, id: Optional[str] = None, name: Optional[str] = None):
        self.identity_obj = Identity(id=id, name=name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.identity_obj.id} name={self.identity_obj.name}>"

    # --- Contract ---
    @abstractmethod
    def identity(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def knowledge(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def history(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def alignment(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def recommendation(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def related_domains(self) -> Iterable[str]:
        raise NotImplementedError

    @abstractmethod
    def related_knowledge(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def related_evidence(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        raise NotImplementedError
