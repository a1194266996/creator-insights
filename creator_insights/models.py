from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class Note:
    source: str
    note_id: str
    title: str
    author_name: str = ""
    author_id: str = ""
    url: str = ""
    keyword: str = ""
    snippet: str = ""
    publish_time: str = ""
    collected_at: str = field(default_factory=utc_now_iso)
    like_count: int = 0
    collect_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    content_type: str = ""
    content_summary: str = ""
    creator_takeaway: str = ""
    raw_json: str = "{}"

    @property
    def engagement(self) -> int:
        return self.like_count + self.collect_count + self.comment_count + self.share_count
