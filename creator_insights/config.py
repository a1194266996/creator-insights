from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    project_root: Path
    db_path: Path
    export_dir: Path
    source: str
    keywords: list[str]
    xhs_export_path: Path | None
    search_site: str
    search_engine: str
    search_user_agent: str
    request_timeout_seconds: int
    feishu_webhook_url: str


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path.cwd()
    _load_dotenv(root / ".env")

    db_path = Path(os.environ.get("CREATOR_INSIGHTS_DB_PATH", "data/creator_insights.db"))
    export_dir = Path(os.environ.get("CREATOR_INSIGHTS_EXPORT_DIR", "exports"))
    export_path = os.environ.get("XHS_EXPORT_PATH")

    if not db_path.is_absolute():
        db_path = root / db_path
    if not export_dir.is_absolute():
        export_dir = root / export_dir

    xhs_export_path = None
    if export_path:
        xhs_export_path = Path(export_path)
        if not xhs_export_path.is_absolute():
            xhs_export_path = root / xhs_export_path

    return Settings(
        project_root=root,
        db_path=db_path,
        export_dir=export_dir,
        source=os.environ.get("CREATOR_INSIGHTS_SOURCE", "web_search").strip(),
        keywords=_csv(os.environ.get("XHS_KEYWORDS", "猫,萌宠")),
        xhs_export_path=xhs_export_path,
        search_site=os.environ.get("SEARCH_SITE", "").strip(),
        search_engine=os.environ.get("SEARCH_ENGINE", "public_search").strip(),
        search_user_agent=os.environ.get(
            "SEARCH_USER_AGENT",
            "Mozilla/5.0 (compatible; CreatorInsightsBot/0.1; public web search)",
        ).strip(),
        request_timeout_seconds=int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "20")),
        feishu_webhook_url=os.environ.get("FEISHU_WEBHOOK_URL", "").strip(),
    )
