from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from creator_insights.config import Settings
from creator_insights.models import Note

from .base import Source


class JsonExportSource(Source):
    def collect(self, settings: Settings, limit: int) -> list[Note]:
        if settings.xhs_export_path is None:
            raise ValueError("Set XHS_EXPORT_PATH in .env when CREATOR_INSIGHTS_SOURCE=json_export")

        path = settings.xhs_export_path
        if not path.exists():
            raise FileNotFoundError(path)

        rows = _read_json_or_jsonl(path)
        notes: list[Note] = []
        for index, row in enumerate(rows[: max(0, limit)]):
            note_id = str(_first(row, "note_id", "id", "noteId", default=f"json-{index + 1}"))
            title = str(_first(row, "title", "desc", "content", default=""))
            keyword = str(_first(row, "keyword", "query", default=""))
            notes.append(
                Note(
                    source="json_export",
                    note_id=note_id,
                    title=title,
                    author_name=str(_first(row, "author_name", "nickname", "user_name", default="")),
                    author_id=str(_first(row, "author_id", "user_id", "userId", default="")),
                    url=str(_first(row, "url", "share_url", "link", default="")),
                    keyword=keyword,
                    publish_time=str(_first(row, "publish_time", "time", "created_at", default="")),
                    like_count=_int(_first(row, "like_count", "likes", "liked_count", default=0)),
                    collect_count=_int(_first(row, "collect_count", "collects", "collected_count", default=0)),
                    comment_count=_int(_first(row, "comment_count", "comments", default=0)),
                    share_count=_int(_first(row, "share_count", "shares", default=0)),
                    raw_json=json.dumps(row, ensure_ascii=False),
                )
            )
        return notes


def _read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "data", "notes", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError(f"Unsupported JSON structure in {path}")


def _first(row: dict[str, Any], *keys: str, default: Any) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return default


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
