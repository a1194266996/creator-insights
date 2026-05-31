from __future__ import annotations

import csv
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .db import connect


def analyze(db_path: Path, export_dir: Path, days: int) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                source, note_id, title, author_name, url, keyword, snippet,
                publish_time, collected_at, like_count, collect_count,
                comment_count, share_count, content_type, content_summary,
                creator_takeaway,
                like_count + collect_count + comment_count + share_count AS engagement
            FROM notes
            WHERE collected_at >= ?
            ORDER BY collected_at DESC
            """,
            (since,),
        ).fetchall()

    output_path = export_dir / f"insights-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    output_path.write_text(render_markdown(rows, days), encoding="utf-8-sig")
    _export_csv(export_dir / "latest-notes.csv", rows)
    return output_path


def latest_rows(db_path: Path, limit: int, days: int, source: str | None = None) -> list[sqlite3.Row]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    source_filter = "AND source = ?" if source else ""
    params: tuple[object, ...] = (since, source, limit) if source else (since, limit)
    with connect(db_path) as conn:
        return conn.execute(
            f"""
            SELECT
                source, note_id, title, author_name, url, keyword, snippet,
                publish_time, collected_at, like_count, collect_count,
                comment_count, share_count, content_type, content_summary,
                creator_takeaway,
                like_count + collect_count + comment_count + share_count AS engagement
            FROM notes
            WHERE collected_at >= ?
            {source_filter}
            ORDER BY collected_at DESC
            LIMIT ?
            """,
            params,
        ).fetchall()


def render_markdown(rows: list[sqlite3.Row], days: int) -> str:
    keyword_counter = Counter(row["keyword"] or "未标记" for row in rows)
    type_counter = Counter(row["content_type"] or "未分析" for row in rows)

    lines = [
        f"# 全网萌宠内容搜索日报（近 {days} 天）",
        "",
        f"- 样本数：{len(rows)}",
        f"- 关键词：{', '.join(keyword_counter.keys()) if keyword_counter else '无'}",
        f"- 内容类型：{', '.join(f'{k} {v}' for k, v in type_counter.most_common()) if type_counter else '无'}",
        "",
        "## 搜索结果与简短分析",
        "",
        "| 序号 | 关键词 | 类型 | 标题 | 简短分析 | 创作启发 |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]

    for rank, row in enumerate(rows[:30], 1):
        title = _cell(row["title"])
        if row["url"]:
            title = f"[{title}]({row['url']})"
        lines.append(
            "| {rank} | {keyword} | {content_type} | {title} | {summary} | {takeaway} |".format(
                rank=rank,
                keyword=_cell(row["keyword"]),
                content_type=_cell(row["content_type"]),
                title=title,
                summary=_cell(row["content_summary"]),
                takeaway=_cell(row["creator_takeaway"]),
            )
        )

    lines.extend(["", "## 今日可参考方向", ""])
    for content_type, count in type_counter.most_common(5):
        lines.append(f"- {content_type}: 搜到 {count} 条，可优先观察标题结构、封面承诺和评论区问题。")

    return "\n".join(lines) + "\n"


def render_feishu_text(rows: list[sqlite3.Row], days: int) -> str:
    if not rows:
        return (
            f"全网萌宠内容搜索日报（近 {days} 天）\n"
            "本次没有收录到可分析的公开搜索结果。\n\n"
            "说明：程序只读取公开搜索索引可见的数据；不会绕过登录、验证码、签名或风控。"
        )

    lines = [
        f"全网萌宠内容搜索日报（近 {days} 天）",
        f"本次收录 {len(rows)} 条公开搜索结果",
        "",
    ]
    for index, row in enumerate(rows[:20], 1):
        lines.extend(
            [
                f"{index}. [{row['keyword']}] {row['title']}",
                f"类型：{row['content_type'] or '未分析'}",
                f"分析：{row['content_summary'] or '暂无'}",
                f"启发：{row['creator_takeaway'] or '暂无'}",
                f"链接：{row['url']}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def _export_csv(path: Path, rows: list[sqlite3.Row]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            [
                "source",
                "note_id",
                "title",
                "author_name",
                "url",
                "keyword",
                "snippet",
                "publish_time",
                "collected_at",
                "like_count",
                "collect_count",
                "comment_count",
                "share_count",
                "content_type",
                "content_summary",
                "creator_takeaway",
                "engagement",
            ]
        )
        writer.writerows([tuple(row) for row in rows])


def _cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()
