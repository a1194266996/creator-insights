from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from .models import Note


SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    source TEXT NOT NULL,
    note_id TEXT NOT NULL,
    title TEXT NOT NULL,
    author_name TEXT NOT NULL DEFAULT '',
    author_id TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    keyword TEXT NOT NULL DEFAULT '',
    publish_time TEXT NOT NULL DEFAULT '',
    collected_at TEXT NOT NULL,
    like_count INTEGER NOT NULL DEFAULT 0,
    collect_count INTEGER NOT NULL DEFAULT 0,
    comment_count INTEGER NOT NULL DEFAULT 0,
    share_count INTEGER NOT NULL DEFAULT 0,
    raw_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (source, note_id)
);

CREATE INDEX IF NOT EXISTS idx_notes_collected_at ON notes(collected_at);
CREATE INDEX IF NOT EXISTS idx_notes_keyword ON notes(keyword);
CREATE INDEX IF NOT EXISTS idx_notes_engagement
ON notes(like_count, collect_count, comment_count, share_count);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_notes(db_path: Path, notes: Iterable[Note]) -> int:
    rows = list(notes)
    if not rows:
        return 0

    with connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO notes (
                source, note_id, title, author_name, author_id, url, keyword,
                publish_time, collected_at, like_count, collect_count,
                comment_count, share_count, raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, note_id) DO UPDATE SET
                title = excluded.title,
                author_name = excluded.author_name,
                author_id = excluded.author_id,
                url = excluded.url,
                keyword = excluded.keyword,
                publish_time = excluded.publish_time,
                collected_at = excluded.collected_at,
                like_count = excluded.like_count,
                collect_count = excluded.collect_count,
                comment_count = excluded.comment_count,
                share_count = excluded.share_count,
                raw_json = excluded.raw_json
            """,
            [
                (
                    note.source,
                    note.note_id,
                    note.title,
                    note.author_name,
                    note.author_id,
                    note.url,
                    note.keyword,
                    note.publish_time,
                    note.collected_at,
                    note.like_count,
                    note.collect_count,
                    note.comment_count,
                    note.share_count,
                    note.raw_json,
                )
                for note in rows
            ],
        )
    return len(rows)
