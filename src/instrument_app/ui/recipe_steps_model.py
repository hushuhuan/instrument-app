from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from instrument_app.domain.recipe_models import BusinessPhase, RecipeStep, business_phase_label
from uuid import uuid4


class RecipeStepsModel(QAbstractListModel):
    """Editable ordered list of `RecipeStep` for the recipe editor (US2)."""

    StepRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._steps: list[RecipeStep] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._steps)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._steps):
            return None
        step = self._steps[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            label = business_phase_label(step.business_phase)
            ov = f" · {step.display_override}" if step.display_override.strip() else ""
            return f"{index.row() + 1}. {label} · {step.plan_duration_sec}s{ov}"
        if role == RecipeStepsModel.StepRole:
            return step
        return None

    def set_steps(self, steps: list[RecipeStep]) -> None:
        self.beginResetModel()
        self._steps = [replace_order(s, i) for i, s in enumerate(steps)]
        self.endResetModel()

    def steps_snapshot(self) -> list[RecipeStep]:
        return list(self._steps)

    def append_new_step(self, phase: BusinessPhase = BusinessPhase.REACTION) -> None:
        row = len(self._steps)
        self.beginInsertRows(QModelIndex(), row, row)
        self._steps.append(
            RecipeStep(
                step_uid=uuid4(),
                order_index=row,
                business_phase=phase,
                plan_duration_sec=300,
                device_args={},
                display_override="",
            )
        )
        self.endInsertRows()

    def remove_rows(self, rows: list[int]) -> None:
        for row in sorted({r for r in rows if 0 <= r < len(self._steps)}, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._steps[row]
            self.endRemoveRows()
        self._renumber()

    def move_up(self, row: int) -> None:
        if row < 1 or row >= len(self._steps):
            return
        self.beginResetModel()
        self._steps[row - 1], self._steps[row] = self._steps[row], self._steps[row - 1]
        self._renumber()
        self.endResetModel()

    def move_down(self, row: int) -> None:
        if row < 0 or row + 1 >= len(self._steps):
            return
        self.beginResetModel()
        self._steps[row + 1], self._steps[row] = self._steps[row], self._steps[row + 1]
        self._renumber()
        self.endResetModel()

    def replace_at(self, row: int, step: RecipeStep) -> None:
        if row < 0 or row >= len(self._steps):
            return
        step = replace_order(step, row)
        self._steps[row] = step
        idx = self.index(row, 0)
        self.dataChanged.emit(idx, idx)

    def _renumber(self) -> None:
        self._steps = [replace_order(s, i) for i, s in enumerate(self._steps)]


def replace_order(step: RecipeStep, order_index: int) -> RecipeStep:
    if step.order_index == order_index:
        return step
    return RecipeStep(
        step_uid=step.step_uid,
        order_index=order_index,
        business_phase=step.business_phase,
        plan_duration_sec=step.plan_duration_sec,
        device_args=dict(step.device_args),
        display_override=step.display_override,
    )
