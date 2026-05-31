from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from creator_insights.config import Settings
from creator_insights.insights import enrich_note
from creator_insights.models import Note

from .base import Source


PET_WORDS = (
    "猫",
    "猫咪",
    "萌宠",
    "宠物",
    "铲屎官",
    "布偶",
    "英短",
    "美短",
    "橘猫",
    "狸花",
    "猫粮",
    "猫砂",
    "养猫",
)

NOISE_WORDS = (
    "字典",
    "汉字",
    "拼音",
    "部首",
    "笔顺",
    "翻译",
    "百科",
    "招聘",
    "游戏下载",
)

NOISE_HOSTS = (
    "so.com",
    "www.so.com",
    "sogou.com",
    "www.sogou.com",
    "bing.com",
    "www.bing.com",
    "baike.baidu.com",
    "zidian.",
    "hanyuguoxue.com",
    "gushici.net",
)


class WebSearchSource(Source):
    def collect(self, settings: Settings, limit: int) -> list[Note]:
        seen: set[str] = set()
        notes: list[Note] = []
        per_keyword = max(8, (limit + max(1, len(settings.keywords)) - 1) // max(1, len(settings.keywords)))

        for keyword in settings.keywords:
            items: list[dict[str, str]] = []
            for query in _build_queries(keyword, settings.search_site):
                items.extend(_search_public_indexes(query, settings, per_keyword * 2))
            for item in items:
                url = _normalize_url(item["url"])
                title = _clean_title(item["title"])
                snippet = _clean_snippet(item["snippet"])
                if not url or url in seen or _is_noise_url(url) or not _is_relevant_pet_content(title, snippet):
                    continue
                seen.add(url)
                note = Note(
                    source="web_search",
                    note_id=_stable_id(url),
                    title=title,
                    url=url,
                    keyword=keyword,
                    snippet=snippet,
                    publish_time=item["publish_time"],
                    raw_json=json.dumps(item, ensure_ascii=False),
                )
                notes.append(enrich_note(note))
                if len(notes) >= limit:
                    return notes

        return notes


def _build_queries(keyword: str, search_site: str) -> list[str]:
    site_part = f"site:{search_site} " if search_site else ""
    general = [
        f"{site_part}{keyword} 猫 萌宠 养猫 帖子 选题",
        f"{site_part}{keyword} 猫咪 日常 文案",
        f"{site_part}{keyword} 养猫 新手 避坑",
        f"{site_part}{keyword} 宠物猫 品种 护理",
        f"{site_part}{keyword} 小红书 宠物 文案",
    ]
    if search_site:
        return general
    return general + [
        f"site:zhihu.com/p {keyword} 猫 萌宠 养猫",
        f"site:sohu.com/a {keyword} 猫 萌宠 宠物猫",
        f"site:mp.weixin.qq.com {keyword} 猫 萌宠 养猫",
        f"site:douban.com/group/topic {keyword} 猫 萌宠",
        f"site:baijiahao.baidu.com {keyword} 猫 萌宠 养猫",
    ]


def _search_public_indexes(query: str, settings: Settings, limit: int) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for searcher in (_search_bing_rss, _search_sogou_html, _search_so_html):
        try:
            items.extend(searcher(query, settings, limit))
        except Exception as exc:
            items.append(
                {
                    "query": query,
                    "title": f"搜索源异常：{searcher.__name__}",
                    "url": "",
                    "snippet": str(exc),
                    "publish_time": "",
                }
            )
    return items


def _search_bing_rss(query: str, settings: Settings, limit: int) -> list[dict[str, str]]:
    params = urllib.parse.urlencode({"q": query, "format": "rss", "count": str(limit), "setlang": "zh-CN"})
    url = f"https://www.bing.com/search?{params}"
    xml_text = _fetch_text(url, settings)
    root = ET.fromstring(xml_text)

    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item")[:limit]:
        items.append(
            {
                "query": query,
                "title": html.unescape(item.findtext("title") or ""),
                "url": html.unescape(item.findtext("link") or ""),
                "snippet": html.unescape(_strip_tags(item.findtext("description") or "")),
                "publish_time": item.findtext("pubDate") or "",
            }
        )
    return items


def _search_sogou_html(query: str, settings: Settings, limit: int) -> list[dict[str, str]]:
    url = "https://www.sogou.com/web?" + urllib.parse.urlencode({"query": query})
    return _search_html(url, query, settings, limit)


def _search_so_html(query: str, settings: Settings, limit: int) -> list[dict[str, str]]:
    url = "https://www.so.com/s?" + urllib.parse.urlencode({"q": query})
    return _search_html(url, query, settings, limit)


def _search_html(url: str, query: str, settings: Settings, limit: int) -> list[dict[str, str]]:
    text = _fetch_text(url, settings)
    anchors = re.findall(r"<a\b[^>]*?href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", text, flags=re.I | re.S)

    items: list[dict[str, str]] = []
    checked = 0
    for raw_href, raw_title in anchors:
        if checked >= 120 or len(items) >= limit:
            break
        checked += 1

        href = html.unescape(raw_href.strip())
        candidate = urllib.parse.urljoin(url, href)
        resolved = _resolve_redirect(candidate, settings)
        if not _looks_like_http_url(resolved):
            continue

        title = _strip_tags(html.unescape(raw_title))
        snippet = _nearby_text(text, raw_href)
        items.append(
            {
                "query": query,
                "title": title,
                "url": resolved,
                "snippet": snippet,
                "publish_time": "",
            }
        )
    return items


def _fetch_text(url: str, settings: Settings) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": settings.search_user_agent})
    with urllib.request.urlopen(request, timeout=settings.request_timeout_seconds) as response:
        return response.read().decode("utf-8", errors="replace")


def _resolve_redirect(url: str, settings: Settings) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if not any(name in host for name in ("sogou.com", "so.com", "bing.com")):
        return url
    try:
        request = urllib.request.Request(url, headers={"User-Agent": settings.search_user_agent})
        with urllib.request.urlopen(request, timeout=min(settings.request_timeout_seconds, 8)) as response:
            return response.geturl()
    except Exception:
        return url


def _stable_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:20]


def _looks_like_http_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _normalize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return ""
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))


def _is_relevant_pet_content(title: str, snippet: str) -> bool:
    text = f"{title} {snippet}"
    if any(word in text for word in NOISE_WORDS):
        return False
    return any(word in text for word in PET_WORDS)


def _is_noise_url(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(noise in host for noise in NOISE_HOSTS)


def _clean_title(title: str) -> str:
    title = re.sub(r"\s*[-_]\s*(小红书|知乎|百度百科|搜狐|微博)\s*$", "", title.strip())
    return title or "未命名萌宠内容"


def _clean_snippet(snippet: str) -> str:
    return re.sub(r"\s+", " ", snippet).strip()


def _nearby_text(page: str, needle: str) -> str:
    index = page.find(needle)
    if index < 0:
        return ""
    start = max(0, index - 800)
    end = min(len(page), index + 1600)
    return _clean_snippet(html.unescape(_strip_tags(page[start:end])))


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")
