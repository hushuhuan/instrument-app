from __future__ import annotations

from datetime import datetime
from pathlib import Path


def debug_device_log_file() -> Path:
    """Append-only audit log for manual/debug device commands (repo CWD / logs)."""
    return Path.cwd() / "logs" / "debug_device.log"


def append_debug_device_log(line: str) -> None:
    path = debug_device_log_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{ts}\t{line.rstrip()}\n")
