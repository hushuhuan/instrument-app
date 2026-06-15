from __future__ import annotations

import math
import time
from datetime import datetime

from instrument_app.hal.interfaces.instrument_hal import AmbientReading


class AmbientSimulator:
    """Deterministic-feeling ambient channel for mock runs."""

    def __init__(self) -> None:
        self._start_ms = time.time()

    def reading(self) -> AmbientReading:
        t = time.time() - self._start_ms
        return AmbientReading(
            temperature_celsius=22.0 + 1.2 * math.sin(t / 31.0),
            humidity_rh=48.0 + 3.0 * math.sin(t / 17.0),
            valid=True,
            timestamp=datetime.now(),
        )

    def health_row(self) -> tuple[str, bool, str]:
        return "环境传感器", True, "仿真读数可用"
