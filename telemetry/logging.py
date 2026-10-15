"""
Structured logger for the runtime. JSON formatting for Cloudflare logs.
"""

import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": int(record.created),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            payload.update(record.extra)
        return json.dumps(payload)

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
