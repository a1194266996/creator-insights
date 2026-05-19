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
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


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

    return Settings(
        project_root=root,
        db_path=db_path,
        export_dir=export_dir,
        source=os.environ.get("CREATOR_INSIGHTS_SOURCE", "sample").strip(),
        keywords=_csv(os.environ.get("XHS_KEYWORDS", "猫,萌宠,布偶猫,英短,橘猫")),
        xhs_export_path=(root / export_path if export_path and not Path(export_path).is_absolute() else Path(export_path))
        if export_path
        else None,
    )
