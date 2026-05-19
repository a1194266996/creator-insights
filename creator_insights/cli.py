from __future__ import annotations

import argparse
import time
from datetime import datetime

from .analysis import analyze
from .config import load_settings
from .db import init_db, upsert_notes
from .sources import get_source


def main() -> None:
    parser = argparse.ArgumentParser(prog="creator-insights")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Create or migrate the SQLite database.")

    collect_parser = subparsers.add_parser("collect", help="Collect notes once.")
    collect_parser.add_argument("--limit", type=int, default=100)
    collect_parser.add_argument("--source", default=None)

    analyze_parser = subparsers.add_parser("analyze", help="Generate an insight report.")
    analyze_parser.add_argument("--days", type=int, default=7)

    daily_once_parser = subparsers.add_parser("daily", help="Run collect+analyze once.")
    daily_once_parser.add_argument("--limit", type=int, default=100)
    daily_once_parser.add_argument("--days", type=int, default=7)

    daily_parser = subparsers.add_parser("run-daily", help="Run collect+analyze every N hours.")
    daily_parser.add_argument("--interval-hours", type=float, default=24)
    daily_parser.add_argument("--limit", type=int, default=100)
    daily_parser.add_argument("--days", type=int, default=7)

    args = parser.parse_args()
    settings = load_settings()

    if args.command == "init-db":
        init_db(settings.db_path)
        print(f"Initialized database: {settings.db_path}")
        return

    if args.command == "collect":
        count = _collect(settings, limit=args.limit, source_name=args.source)
        print(f"Collected {count} notes into {settings.db_path}")
        return

    if args.command == "analyze":
        output_path = analyze(settings.db_path, settings.export_dir, days=args.days)
        print(f"Generated report: {output_path}")
        return

    if args.command == "daily":
        count = _collect(settings, limit=args.limit)
        output_path = analyze(settings.db_path, settings.export_dir, days=args.days)
        print(f"Collected {count} notes. Generated report: {output_path}")
        return

    if args.command == "run-daily":
        _run_daily(args.interval_hours, args.limit, args.days)
        return


def _collect(settings, limit: int, source_name: str | None = None) -> int:
    init_db(settings.db_path)
    source = get_source(source_name or settings.source)
    notes = source.collect(settings, limit=limit)
    return upsert_notes(settings.db_path, notes)


def _run_daily(interval_hours: float, limit: int, days: int) -> None:
    if interval_hours <= 0:
        raise ValueError("--interval-hours must be greater than 0")

    while True:
        settings = load_settings()
        print(f"[{datetime.now().isoformat(timespec='seconds')}] collecting...")
        count = _collect(settings, limit=limit)
        output_path = analyze(settings.db_path, settings.export_dir, days=days)
        print(f"Collected {count} notes. Generated report: {output_path}")
        time.sleep(interval_hours * 60 * 60)
