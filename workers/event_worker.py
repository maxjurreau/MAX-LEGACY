"""
Event worker: consumes events from the event queue and coordinates MDT and QCE
processing and the Event Engine.
This script is intentionally minimal — it demonstrates flow and retries.
"""

import os
import time
import json
from ..queues.event_queue import EventQueue
from ..queues.mdt_queue import MDTQueue
from ..queues.qce_queue import QCEQueue
from ..telemetry.logging import get_logger
from ..r2.storage_adapter import R2StorageAdapter

logger = get_logger("event_worker")
EVENT_QUEUE = EventQueue(binding_name=os.getenv("EVENT_QUEUE", "EVENT_QUEUE"))
MDT_QUEUE = MDTQueue()
QCE_QUEUE = QCEQueue()
R2 = R2StorageAdapter(bucket_name=os.getenv("R2_BUCKET", "max-legacy-r2"))

def process_event(event):
    logger.info("processing_event", extra={"event": event})
    # 1. Enqueue for MDT
    MDT_QUEUE.enqueue(event)
    # 2. Enqueue for QCE
    QCE_QUEUE.enqueue(event)
    # 3. Persist raw event to R2 for evidence
    key = f"events/{int(time.time())}_{event.get('id', 'noid')}.json"
    R2.put_object(key, json.dumps(event).encode("utf-8"), content_type="application/json")
    # 4. Acknowledge or emit follow-up events as needed
    logger.info("event_processed", extra={"key": key})

def run_once():
    item = EVENT_QUEUE.dequeue(timeout=1.0)
    if not item:
        return False
    try:
        process_event(item)
    except Exception as e:
        logger.exception("failed_processing_event", exc_info=e)
        # Optionally re-enqueue or route to dead-letter
    return True

def run_forever():
    logger.info("event_worker_started")
    while True:
        processed = run_once()
        if not processed:
            time.sleep(0.5)

if __name__ == "__main__":
    run_forever()
