from __future__ import annotations

from .base import Source
from .json_export import JsonExportSource
from .sample import SampleSource
from .web_search import WebSearchSource


def get_source(name: str) -> Source:
    normalized = name.strip().lower().replace("-", "_")
    if normalized == "sample":
        return SampleSource()
    if normalized == "json_export":
        return JsonExportSource()
    if normalized == "web_search":
        return WebSearchSource()
    raise ValueError(f"Unknown source: {name}")


__all__ = ["Source", "get_source"]
