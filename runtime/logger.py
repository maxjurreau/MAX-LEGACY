"""runtime/logger.py

Simple logging setup for MAX-LEGACY runtime.
Provides a get_logger() factory and a configure_root_logger() helper.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

_DEFAULT_LOG_LEVEL = os.getenv("MAX_LOG_LEVEL", "INFO").upper()


def configure_root_logger(level: Optional[str] = None) -> None:
    """Configure the root logger for simple stdout structured logging.

    This is idempotent and safe to call multiple times.
    """
    if level is None:
        level = _DEFAULT_LOG_LEVEL

    root = logging.getLogger()
    if root.handlers:
        # Assume already configured
        return

    root.setLevel(level)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)

    fmt = os.getenv(
        "MAX_LOG_FORMAT",
        "%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    datefmt = os.getenv("MAX_LOG_DATEFMT", "%Y-%m-%dT%H:%M:%S")
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger for the given name.

    Ensures the root logger is configured before returning.
    """
    configure_root_logger()
    return logging.getLogger(name)
