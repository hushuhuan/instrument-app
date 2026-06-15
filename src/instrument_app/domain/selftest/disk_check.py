from __future__ import annotations

import shutil
from pathlib import Path

from instrument_app.domain.app_config import AppConfig


def check_disk_space(cfg: AppConfig) -> tuple[bool, str]:
    """Return (ok, message) using ``shutil.disk_usage`` on configured or default path."""
    path = cfg.selftest_disk_path
    if not path:
        path = str(Path.cwd())
    try:
        usage = shutil.disk_usage(path)
    except OSError as e:
        return False, f"无法读取磁盘空间 ({path}): {e}"
    free = usage.free
    need = cfg.selftest_min_free_bytes
    if free >= need:
        mib = free // (1024 * 1024)
        return True, f"{path} 可用约 {mib} MiB（≥ 阈值）"
    return (
        False,
        f"可用空间不足：{free} 字节 < 所需 {need} 字节",
    )
