from __future__ import annotations

from typing import Any, Dict


class RenderLayer:
    """Prepare runtime artifacts for rendering (UI-friendly shapes)."""

    def __init__(self, root: Optional[str] = None):
        pass

    def render_knowledge_card(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        return {"card": {"title": summary.get("title"), "id": summary.get("id"), "meta": {"domain": summary.get("domain")}}}
