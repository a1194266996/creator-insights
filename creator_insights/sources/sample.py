from __future__ import annotations

import json
from random import Random

from creator_insights.config import Settings
from creator_insights.models import Note

from .base import Source


class SampleSource(Source):
    def collect(self, settings: Settings, limit: int) -> list[Note]:
        rng = Random(20260519)
        notes: list[Note] = []
        themes = [
            ("猫咪日常", "用连续剧情留住粉丝"),
            ("新手养猫", "把痛点拆成清单"),
            ("猫粮测评", "用对比表降低决策成本"),
            ("布偶猫护理", "突出高颜值和护理难点"),
            ("猫玩具", "用实拍反应制造转发点"),
        ]

        for index in range(max(0, limit)):
            keyword = settings.keywords[index % len(settings.keywords)] if settings.keywords else "猫"
            theme, angle = themes[index % len(themes)]
            likes = rng.randint(80, 5000)
            collects = rng.randint(10, 1500)
            comments = rng.randint(5, 500)
            shares = rng.randint(1, 300)
            payload = {
                "theme": theme,
                "angle": angle,
                "keyword": keyword,
                "sample": True,
            }
            notes.append(
                Note(
                    source="sample",
                    note_id=f"sample-{index + 1:04d}",
                    title=f"{keyword}｜{theme}：{angle}",
                    author_name=f"萌宠账号{index % 7 + 1}",
                    author_id=f"sample-author-{index % 7 + 1}",
                    url="",
                    keyword=keyword,
                    like_count=likes,
                    collect_count=collects,
                    comment_count=comments,
                    share_count=shares,
                    raw_json=json.dumps(payload, ensure_ascii=False),
                )
            )
        return notes

