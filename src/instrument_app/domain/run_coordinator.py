from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from PySide6.QtCore import QObject, QTimer, Signal

from instrument_app.domain.app_config import AppConfig
from instrument_app.domain.phase_script_router import step_duration_ms
from instrument_app.domain.recipe_models import Recipe, step_status_line
from instrument_app.domain.run_models import RunSessionPhase, RunState
from instrument_app.hal.interfaces.instrument_hal import InstrumentHal
from instrument_app.logging.alarm_log import append_alarm


class RunCoordinator(QObject):
    run_phase_changed = Signal(object)
    step_progress = Signal(int, int, str)
    remaining_seconds_changed = Signal(int)
    run_finished = Signal(object)

    def __init__(self, cfg: AppConfig, hal: InstrumentHal, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._hal = hal
        self._state = RunState(phase=RunSessionPhase.IDLE)
        self._active_recipe: Recipe | None = None
        self._remaining_sec = 0
        self._self_test_active = False

    def phase(self) -> RunSessionPhase:
        return self._state.phase

    def is_idle(self) -> bool:
        return self._state.phase in (
            RunSessionPhase.IDLE,
            RunSessionPhase.COMPLETED,
            RunSessionPhase.FAILED,
        )

    def set_self_test_active(self, v: bool) -> None:
        self._self_test_active = v

    @property
    def self_test_active(self) -> bool:
        return self._self_test_active

    def start_run(self, recipe: Recipe) -> None:
        if self._self_test_active:
            self.run_finished.emit(RunSessionPhase.FAILED)
            return
        if not self.is_idle():
            return
        if not recipe.steps:
            append_alarm("run_invalid", "拒绝启动：方法步骤为空")
            self._state.phase = RunSessionPhase.FAILED
            self.run_phase_changed.emit(self._state.phase)
            self.run_finished.emit(RunSessionPhase.FAILED)
            return

        self._active_recipe = recipe
        self._state = RunState(
            id=uuid4(),
            recipe_id=recipe.id,
            started_at=datetime.now(),
            phase=RunSessionPhase.RUNNING,
            current_step_index=0,
            step_statuses=["pending"] * len(recipe.steps),
        )
        self._state.step_statuses[0] = "running"
        self._remaining_sec = sum(s.plan_duration_sec for s in recipe.steps)

        self.run_phase_changed.emit(self._state.phase)
        self.step_progress.emit(
            0,
            len(recipe.steps),
            step_status_line(recipe.steps[0]),
        )
        self.remaining_seconds_changed.emit(self._remaining_sec)
        self._schedule_next_step()

    def abort_run(self) -> None:
        if self._state.phase not in (RunSessionPhase.RUNNING, RunSessionPhase.PAUSED):
            return
        self._state.phase = RunSessionPhase.FAILED
        self._state.ended_at = datetime.now()
        self._active_recipe = None
        append_alarm("run_aborted", "运行已被中止")
        self.run_phase_changed.emit(self._state.phase)
        self.run_finished.emit(RunSessionPhase.FAILED)

    def _schedule_next_step(self) -> None:
        recipe = self._active_recipe
        if recipe is None:
            return
        idx = self._state.current_step_index
        if idx >= len(recipe.steps):
            self._state.phase = RunSessionPhase.COMPLETED
            self._state.ended_at = datetime.now()
            self.run_phase_changed.emit(self._state.phase)
            self.remaining_seconds_changed.emit(0)
            self.run_finished.emit(RunSessionPhase.COMPLETED)
            self._active_recipe = None
            return

        step = recipe.steps[idx]
        delay_ms = step_duration_ms(step, self._cfg, self._hal)

        def on_timeout() -> None:
            if self._state.phase != RunSessionPhase.RUNNING:
                return
            rec = self._active_recipe
            if rec is None:
                return
            done_idx = self._state.current_step_index
            if 0 <= done_idx < len(rec.steps):
                self._state.step_statuses[done_idx] = "success"
                self._remaining_sec = max(
                    0, self._remaining_sec - rec.steps[done_idx].plan_duration_sec
                )
            self._state.current_step_index += 1
            if self._state.current_step_index >= len(rec.steps):
                self._state.phase = RunSessionPhase.COMPLETED
                self._state.ended_at = datetime.now()
                self.run_phase_changed.emit(self._state.phase)
                self.remaining_seconds_changed.emit(0)
                self.run_finished.emit(RunSessionPhase.COMPLETED)
                self._active_recipe = None
                return
            self._state.step_statuses[self._state.current_step_index] = "running"
            self.step_progress.emit(
                self._state.current_step_index,
                len(rec.steps),
                step_status_line(rec.steps[self._state.current_step_index]),
            )
            self.remaining_seconds_changed.emit(self._remaining_sec)
            self._schedule_next_step()

        QTimer.singleShot(delay_ms, on_timeout)
