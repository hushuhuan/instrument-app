from __future__ import annotations

from instrument_app.domain.app_config import AppConfig, ApplicationRunMode
from instrument_app.domain.run_coordinator import RunCoordinator
from instrument_app.hal.mock.mock_instrument_hal import MockInstrumentHal
from instrument_app.hal.real.real_instrument_hal import RealInstrumentHal


class ApplicationContext:
    def __init__(self, argv: list[str] | None) -> None:
        self.config = AppConfig.from_argv(argv)
        if self.config.run_mode == ApplicationRunMode.MOCK:
            self._hal: MockInstrumentHal | RealInstrumentHal = MockInstrumentHal(
                self.config.mock_time_scale
            )
        else:
            self._hal = RealInstrumentHal()
        self.run_coordinator = RunCoordinator(self.config, self._hal)

    @property
    def hal(self) -> MockInstrumentHal | RealInstrumentHal:
        return self._hal
