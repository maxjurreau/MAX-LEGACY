"""
Event queue abstraction.
Default implementation: in-memory queue for local testing.
In production, replace with Cloudflare Queues or Durable Objects.
"""

import os
import queue
import logging
from typing import Any, Optional

logger = logging.getLogger("event_queue")

class EventQueue:
    def __init__(self, binding_name: str = "EVENT_QUEUE"):
        self.binding_name = binding_name
        # Use process-global queue for simple deployments / tests
        self._q = queue.Queue()

    def enqueue(self, item: Any):
        logger.debug("enqueue", extra={"binding": self.binding_name})
        self._q.put(item)

    def dequeue(self, timeout: float = 0.0) -> Optional[Any]:
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

    def size(self) -> int:
        return self._q.qsize()
