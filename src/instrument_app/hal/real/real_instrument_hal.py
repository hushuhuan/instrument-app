from __future__ import annotations

from datetime import datetime

from instrument_app.hal.interfaces.instrument_hal import AmbientReading


class RealInstrumentHal:
    """Production HAL placeholder until vendor hardware is integrated (T042)."""

    _BUILD = "real-hal-stub-0.1"

    @staticmethod
    def _ni(operation: str) -> tuple[bool, str]:
        return (
            False,
            f"RealInstrumentHal({RealInstrumentHal._BUILD}): 「{operation}」尚未对接现场硬件 — 参见 US3 / plan.md。",
        )

    def ambient_reading(self) -> AmbientReading:
        return AmbientReading(valid=False, timestamp=datetime.now())

    def simulate_reaction_step_ms(
        self, plan_duration_sec: int, mock_time_scale_divisor: int
    ) -> int:
        return 0

    def init_pumps(self) -> tuple[bool, str]:
        return self._ni("泵初始化")

    def init_rotary_valve(self) -> tuple[bool, str]:
        return self._ni("旋转阀初始化")

    def home_stepper(self) -> tuple[bool, str]:
        return self._ni("步进回零")

    def chiller_handshake(self) -> tuple[bool, str]:
        return self._ni("冷机通讯/握手")

    def device_health_summary(self) -> list[tuple[str, bool, str]]:
        reason = "真机 HAL 未接入，无法汇总设备健康"
        return [
            ("环境传感器", False, reason),
            ("注射泵", False, reason),
            ("旋转阀", False, reason),
            ("步进轴", False, reason),
            ("温控/冷机", False, reason),
        ]

    def debug_pump_command(self, action: str, flow_ul_per_min: float) -> tuple[bool, str]:
        return self._ni(f"调试-注射泵({action})")

    def debug_rotary_valve_goto_channel(self, channel: int) -> tuple[bool, str]:
        return self._ni(f"调试-旋转阀通道({channel})")

    def debug_chiller_set_setpoint(self, setpoint_celsius: float) -> tuple[bool, str]:
        return self._ni(f"调试-冷机设定({setpoint_celsius}°C)")

    def debug_chiller_read_setpoint(self) -> tuple[float | None, str]:
        _, msg = self._ni("调试-冷机读回")
        return None, msg
