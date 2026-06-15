from __future__ import annotations

import os
from enum import Enum, auto


class ApplicationRunMode(Enum):
    PRODUCTION = auto()
    MOCK = auto()


class AppConfig:
    def __init__(self) -> None:
        self.run_mode: ApplicationRunMode = ApplicationRunMode.PRODUCTION
        self.mock_time_scale: int = 30
        # Self-test (FR-015 / plan): optional TCP target "host:port"; weak check if empty.
        self.selftest_ping_host: str = ""
        self.selftest_min_free_bytes: int = 1024**3
        self.selftest_disk_path: str | None = None

    @classmethod
    def from_argv(cls, argv: list[str] | None) -> AppConfig:
        cfg = cls()
        if not argv:
            return cfg
        cli_mock = "--mock" in argv
        env_mock = os.environ.get("INSTRUMENT_USE_MOCK", "").strip().lower() in (
            "1",
            "true",
        )
        if cli_mock:
            cfg.run_mode = ApplicationRunMode.MOCK
        elif env_mock:
            cfg.run_mode = ApplicationRunMode.MOCK
        return cfg
