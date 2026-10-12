"""Configuration helpers for MAX-LEGACY runtime."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RuntimeConfig:
    """Central runtime configuration for a MAX-LEGACY process."""

    repo_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    log_level: str = field(default_factory=lambda: os.getenv("MAX_LOG_LEVEL", "INFO").upper())
    default_domain: str = field(default_factory=lambda: os.getenv("MAX_DEFAULT_DOMAIN", "Knowledge"))
    event_store_dir: Path = field(init=False)
    knowledge_store_dir: Path = field(init=False)
    audit_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.event_store_dir = self.repo_root / "events"
        self.knowledge_store_dir = self.repo_root / "knowledge"
        self.audit_path = self.repo_root / "runtime" / "audit_log.jsonl"
        self.event_store_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_store_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        return cls(
            repo_root=Path(os.getenv("MAX_REPO_ROOT", Path(__file__).resolve().parents[1])),
            log_level=os.getenv("MAX_LOG_LEVEL", "INFO").upper(),
            default_domain=os.getenv("MAX_DEFAULT_DOMAIN", "Knowledge"),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "repo_root": str(self.repo_root),
            "log_level": self.log_level,
            "default_domain": self.default_domain,
            "event_store_dir": str(self.event_store_dir),
            "knowledge_store_dir": str(self.knowledge_store_dir),
            "audit_path": str(self.audit_path),
        }


DEFAULT_CONFIG = RuntimeConfig()
