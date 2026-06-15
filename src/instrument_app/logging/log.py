from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def selftest_log_file() -> Path:
    return Path.cwd() / "logs" / "selftest.log"


def append_selftest_summary_line(text: str) -> None:
    """Append one human-readable line to ``logs/selftest.log`` (FR-017)."""
    path = selftest_log_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{ts}\t{text.rstrip()}\n")


def append_selftest_report_json(report: dict) -> None:
    """Append a single-line JSON document per run (aligns with schema-backed reports)."""
    append_selftest_summary_line(json.dumps(report, ensure_ascii=False))
