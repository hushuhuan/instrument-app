from __future__ import annotations

from instrument_app.hal.mock.ambient_sim import AmbientSimulator
from instrument_app.hal.mock.mock_chiller import MockChillerSubsystem
from instrument_app.hal.mock.mock_pump import MockPumpSubsystem
from instrument_app.hal.mock.mock_stepper import MockStepperSubsystem
from instrument_app.hal.mock.mock_valve import MockRotaryValveSubsystem
from instrument_app.hal.mock.reaction_timing import mock_reaction_step_ms


class MockInstrumentHal:
    """Aggregate mock HAL composed of subsystems (T040)."""

    def __init__(self, mock_time_scale_divisor: int = 30) -> None:
        div = mock_time_scale_divisor if mock_time_scale_divisor > 0 else 30
        self._default_scale = div
        self._ambient = AmbientSimulator()
        self._pump = MockPumpSubsystem()
        self._valve = MockRotaryValveSubsystem()
        self._stepper = MockStepperSubsystem()
        self._chiller = MockChillerSubsystem()

    def ambient_reading(self):
        return self._ambient.reading()

    def simulate_reaction_step_ms(
        self, plan_duration_sec: int, mock_time_scale_divisor: int
    ) -> int:
        return mock_reaction_step_ms(
            plan_duration_sec, mock_time_scale_divisor, self._default_scale
        )

    def init_pumps(self) -> tuple[bool, str]:
        return self._pump.init_pumps()

    def init_rotary_valve(self) -> tuple[bool, str]:
        return self._valve.init_rotary_valve()

    def home_stepper(self) -> tuple[bool, str]:
        return self._stepper.home_stepper()

    def chiller_handshake(self) -> tuple[bool, str]:
        return self._chiller.chiller_handshake()

    def debug_pump_command(self, action: str, flow_ul_per_min: float) -> tuple[bool, str]:
        return self._pump.debug_pump_command(action, flow_ul_per_min)

    def debug_rotary_valve_goto_channel(self, channel: int) -> tuple[bool, str]:
        return self._valve.debug_rotary_valve_goto_channel(channel)

    def debug_chiller_set_setpoint(self, setpoint_celsius: float) -> tuple[bool, str]:
        return self._chiller.debug_chiller_set_setpoint(setpoint_celsius)

    def debug_chiller_read_setpoint(self) -> tuple[float | None, str]:
        return self._chiller.debug_chiller_read_setpoint()

    def device_health_summary(self) -> list[tuple[str, bool, str]]:
        return [
            self._ambient.health_row(),
            self._pump.health_row(),
            self._valve.health_row(),
            self._stepper.health_row(),
            self._chiller.health_row(),
        ]
