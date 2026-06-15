from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def alarm_log_file() -> Path:
    return Path.cwd() / "logs" / "alarms.log"


def append_alarm(
    code: str,
    message: str,
    *,
    severity: str = "warn",
    extra: dict | None = None,
) -> None:
    """Append one structured line for FR-009 (JSON per line)."""
    path = alarm_log_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "severity": severity,
        "code": code,
        "message": message,
    }
    if extra:
        payload["extra"] = extra
    line = json.dumps(payload, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
