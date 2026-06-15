from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class AmbientReading:
    temperature_celsius: float = 20.0
    humidity_rh: float = 50.0
    valid: bool = True
    timestamp: datetime | None = None


class InstrumentHal(Protocol):
    def ambient_reading(self) -> AmbientReading: ...
    def simulate_reaction_step_ms(
        self, plan_duration_sec: int, mock_time_scale_divisor: int
    ) -> int: ...
    def init_pumps(self) -> tuple[bool, str]: ...
    def init_rotary_valve(self) -> tuple[bool, str]: ...
    def home_stepper(self) -> tuple[bool, str]: ...
    def chiller_handshake(self) -> tuple[bool, str]: ...

    def device_health_summary(self) -> list[tuple[str, bool, str]]:
        """Subsystem label, healthy flag, human detail (FR-008)."""
        ...

    # Debug / manual bench (v1); channel maps & limits in product config later.
    def debug_pump_command(
        self, action: str, flow_ul_per_min: float
    ) -> tuple[bool, str]:
        """action: 'prime' | 'dispense' | 'stop'; flow_ul_per_min for dispense rate."""
        ...

    def debug_rotary_valve_goto_channel(self, channel: int) -> tuple[bool, str]:
        """0-based channel index."""
        ...

    def debug_chiller_set_setpoint(self, setpoint_celsius: float) -> tuple[bool, str]:
        """Set temperature setpoint (°C)."""
        ...

    def debug_chiller_read_setpoint(self) -> tuple[float | None, str]:
        """(last setpoint °C or None, message)."""
        ...
