from __future__ import annotations

from .models import Note


TYPE_RULES = [
    ("养猫知识", ("新手", "养猫", "驱虫", "疫苗", "绝育", "喂养", "猫粮", "猫砂", "护理")),
    ("好物测评", ("测评", "推荐", "平替", "开箱", "猫粮", "罐头", "冻干", "猫砂", "玩具")),
    ("品种内容", ("布偶", "英短", "美短", "橘猫", "暹罗", "缅因", "狸花", "奶牛猫")),
    ("日常剧情", ("日常", "vlog", "记录", "回家", "睡觉", "撒娇", "捣乱", "铲屎官")),
    ("情绪共鸣", ("治愈", "可爱", "崩溃", "离谱", "笑死", "心软", "陪伴", "打工人")),
    ("领养救助", ("领养", "救助", "流浪", "找家", "送养", "绝育", "救猫")),
]


def enrich_note(note: Note) -> Note:
    text = f"{note.title} {note.snippet}".lower()
    content_type = _content_type(text)
    summary = _summary(note.title, note.snippet, content_type)
    takeaway = _takeaway(content_type)

    return Note(
        source=note.source,
        note_id=note.note_id,
        title=note.title,
        author_name=note.author_name,
        author_id=note.author_id,
        url=note.url,
        keyword=note.keyword,
        snippet=note.snippet,
        publish_time=note.publish_time,
        collected_at=note.collected_at,
        like_count=note.like_count,
        collect_count=note.collect_count,
        comment_count=note.comment_count,
        share_count=note.share_count,
        content_type=content_type,
        content_summary=summary,
        creator_takeaway=takeaway,
        raw_json=note.raw_json,
    )


def _content_type(text: str) -> str:
    scores: list[tuple[int, str]] = []
    for label, words in TYPE_RULES:
        score = sum(1 for word in words if word.lower() in text)
        if score:
            scores.append((score, label))
    if not scores:
        return "萌宠泛内容"
    return sorted(scores, reverse=True)[0][1]


def _summary(title: str, snippet: str, content_type: str) -> str:
    base = _compact(snippet) or _compact(title)
    if len(base) > 70:
        base = base[:67] + "..."
    if content_type == "萌宠泛内容":
        return f"围绕猫/萌宠主题做内容呈现，重点可从标题和封面判断。{base}"
    return f"这条内容偏「{content_type}」，核心信息是：{base}"


def _takeaway(content_type: str) -> str:
    mapping = {
        "养猫知识": "适合拆成清单、避坑、步骤教程，标题里直接点出人群和痛点。",
        "好物测评": "适合做对比表、真实使用反馈和价格/成分差异，提升收藏价值。",
        "品种内容": "适合绑定具体品种、颜值卖点和护理难点，方便精准吸引同类养猫人。",
        "日常剧情": "适合连续更新同一只猫的性格和固定场景，培养追更感。",
        "情绪共鸣": "适合突出反差、治愈或好笑瞬间，让观众快速产生转发理由。",
        "领养救助": "适合交代时间线、健康状态和后续变化，增强信任与情绪投入。",
        "萌宠泛内容": "建议继续观察封面、标题句式和评论区问题，提炼可复用选题。",
    }
    return mapping[content_type]


def _compact(text: str) -> str:
    return " ".join((text or "").split())
