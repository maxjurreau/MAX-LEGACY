from __future__ import annotations

from api.routes import router_for_main as router

# Re-export the shared router so the package remains modular while keeping
# the existing API behavior intact.
__all__ = ["router"]
