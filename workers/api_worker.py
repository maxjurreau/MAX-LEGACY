"""
API worker exposing endpoints listed in the architecture document.
Implements small handlers that call into adapters (D1, R2, Queues).
Keep logic here minimal; push heavy work to workers/event_worker.py and queues.
"""

import os
import json
from typing import Dict, Any

# Lightweight HTTP handler for Cloudflare Python runtime:
# Cloudflare's Python worker environment exposes an HTTP handler differently depending on runtime.
# This file is a minimal WSGI-like style so it can be adapted to the Cloudflare Python worker entrypoint.
# For local development, use `uvicorn` + FastAPI/Starlette and map these handlers.


def _json_response(status: int, body: Dict[str, Any]):
    return ("application/json", status, json.dumps(body).encode("utf-8"))


# Simple in-process adapters (to be swapped for cloud bindings)
# Use absolute imports so modules resolve correctly when the worker is packaged as a top-level module.
from r2.storage_adapter import R2StorageAdapter
from queues.event_queue import EventQueue

R2 = R2StorageAdapter(bucket_name=os.getenv("R2_BUCKET", "max-legacy-r2"))
EVENT_QUEUE = EventQueue(binding_name=os.getenv("EVENT_QUEUE", "EVENT_QUEUE"))


def handle_health(environ, start_response):
    content_type, status, payload = _json_response(200, {"status": "ok", "service": "MAX-LEGACY Cloudflare Runtime"})
    start_response(f"{status} OK", [("Content-Type", content_type)])
    return [payload]


def handle_knowledge(environ, start_response):
    items = R2.list_objects(prefix="knowledge/")
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"count": len(items), "items": items}).encode()]


def handle_events(environ, start_response):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(length) if length else b""
        data = json.loads(body.decode() or "{}")
    except Exception:
        data = {}
    EVENT_QUEUE.enqueue(data)
    start_response("202 Accepted", [("Content-Type", "application/json")])
    return [json.dumps({"enqueued": True}).encode()]


def handle_customers(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"customers": []}).encode()]


def handle_projects(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"projects": []}).encode()]


def handle_revenue(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"revenue": []}).encode()]


def handle_capabilities(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"capabilities": []}).encode()]


def handle_simulations(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"simulations": []}).encode()]


def handle_reality(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"reality": []}).encode()]


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    if path == "/health":
        return handle_health(environ, start_response)
    if path.startswith("/knowledge"):
        return handle_knowledge(environ, start_response)
    if path.startswith("/events") and method in ("POST",):
        return handle_events(environ, start_response)
    if path.startswith("/customers"):
        return handle_customers(environ, start_response)
    if path.startswith("/projects"):
        return handle_projects(environ, start_response)
    if path.startswith("/revenue"):
        return handle_revenue(environ, start_response)
    if path.startswith("/capabilities"):
        return handle_capabilities(environ, start_response)
    if path.startswith("/simulations"):
        return handle_simulations(environ, start_response)
    if path.startswith("/reality"):
        return handle_reality(environ, start_response)
    start_response("404 Not Found", [("Content-Type", "application/json")])
    return [json.dumps({"error": "not_found"}).encode()]
