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
                source, note_id, title, author_name, url, keyword, publish_time, collected_at,
                like_count, collect_count, comment_count, share_count,
                like_count + collect_count + comment_count + share_count AS engagement
            FROM notes
            WHERE collected_at >= ?
            ORDER BY engagement DESC, collected_at DESC
            """,
            (since,),
        ).fetchall()

    output_path = export_dir / f"insights-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    output_path.write_text(_render_markdown(rows, days), encoding="utf-8-sig")
    _export_csv(export_dir / "latest-notes.csv", rows)
    return output_path


def _render_markdown(rows: list[sqlite3.Row], days: int) -> str:
    keyword_counter = Counter(row["keyword"] or "未标记" for row in rows)
    author_counter = Counter(row["author_name"] or "未知作者" for row in rows)

    lines = [
        f"# 萌宠猫内容观察报告（近 {days} 天）",
        "",
        f"- 样本数：{len(rows)}",
        f"- 关键词覆盖：{len(keyword_counter)}",
        "",
        "## 高互动笔记 Top 20",
        "",
        "| 排名 | 标题 | 作者 | 关键词 | 互动量 | 赞 | 藏 | 评 | 转 |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for rank, row in enumerate(rows[:20], 1):
        title = _cell(row["title"])
        if row["url"]:
            title = f"[{title}]({row['url']})"
        lines.append(
            "| {rank} | {title} | {author} | {keyword} | {engagement} | {likes} | "
            "{collects} | {comments} | {shares} |".format(
                rank=rank,
                title=title,
                author=_cell(row["author_name"]),
                keyword=_cell(row["keyword"]),
                engagement=row["engagement"],
                likes=row["like_count"],
                collects=row["collect_count"],
                comments=row["comment_count"],
                shares=row["share_count"],
            )
        )

    lines.extend(["", "## 关键词热度", ""])
    for keyword, count in keyword_counter.most_common(20):
        lines.append(f"- {keyword}: {count}")

    lines.extend(["", "## 高频作者", ""])
    for author, count in author_counter.most_common(20):
        lines.append(f"- {author}: {count}")

    lines.extend(
        [
            "",
            "## 选题观察问题",
            "",
            "- 哪些标题把猫的品种、场景、情绪或养护问题说得最具体？",
            "- 收藏高但评论低的内容，是否更适合做清单、测评和教程？",
            "- 评论高的内容里，粉丝是在提问、共鸣、争议，还是晒自家猫？",
            "- 高互动作者的更新频率、封面结构、标题句式是否有稳定模板？",
        ]
    )
    return "\n".join(lines) + "\n"


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
                "publish_time",
                "collected_at",
                "like_count",
                "collect_count",
                "comment_count",
                "share_count",
                "engagement",
            ]
        )
        writer.writerows([tuple(row) for row in rows])


def _cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()
