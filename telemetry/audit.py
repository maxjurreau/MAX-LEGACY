"""
Audit event recording. Use a durable store for production (D1 or R2).
"""

import time
from .logging import get_logger
logger = get_logger("audit")

def record_audit(event_type: str, details: dict):
    blob = {
        "type": event_type,
        "details": details,
        "ts": int(time.time())
    }
    # For now, log the audit event; production should persist to D1 or R2.
    logger.info("audit_event", extra={"extra": blob})
