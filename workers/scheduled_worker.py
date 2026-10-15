"""
Scheduled worker for maintenance tasks.
Triggered by Cloudflare cron binding (see wrangler.toml).
"""

import os
import time
from ..telemetry.metrics import Metrics
from ..telemetry.logging import get_logger
from ..r2.storage_adapter import R2StorageAdapter

logger = get_logger("scheduled_worker")
metrics = Metrics()
R2 = R2StorageAdapter(bucket_name=os.getenv("R2_BUCKET", "max-legacy-r2"))

def cleanup_old_reports(days=30):
    logger.info("cleanup_start", extra={"days": days})
    objs = R2.list_objects(prefix="reports/")
    now = int(time.time())
    removed = 0
    for o in objs:
        # expect object dict {key, size, last_modified}
        if "last_modified" in o:
            age_days = (now - o["last_modified"]) / 86400
            if age_days > days:
                R2.delete_object(o["key"])
                removed += 1
    logger.info("cleanup_done", extra={"removed": removed})

def generate_report():
    # Placeholder: create a small report and store to R2
    payload = {"timestamp": int(time.time()), "simulations": 0}
    key = f"reports/report_{int(time.time())}.json"
    R2.put_object(key, json.dumps(payload).encode("utf-8"), content_type="application/json")
    metrics.increment("reports_generated")
    logger.info("report_generated", extra={"key": key})

def aggregate_metrics():
    # Placeholder: metrics aggregation hook
    logger.info("aggregate_metrics_start")
    # export or push to monitoring backend
    logger.info("aggregate_metrics_done")

def run_scheduled():
    cleanup_old_reports()
    generate_report()
    aggregate_metrics()

if __name__ == "__main__":
    run_scheduled()
