from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from instrument_app.domain.recipe_models import BusinessPhase, RecipeStep, business_phase_label
from instrument_app.ui.recipe_steps_model import RecipeStepsModel


class RecipeEditorWidget(QWidget):
    """FR-013: edit recipe steps (phase, duration, optional display override)."""

    def __init__(self, model: RecipeStepsModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._model = model
        self._syncing = False

        root = QHBoxLayout(self)
        left = QVBoxLayout()
        self._list = QListView(self)
        self._list.setModel(model)
        self._list.selectionModel().currentRowChanged.connect(self._on_row_changed)
        left.addWidget(QLabel("方法步骤", self))
        left.addWidget(self._list, stretch=1)

        row_btns = QHBoxLayout()
        b_add = QPushButton("添加", self)
        b_rm = QPushButton("删除", self)
        b_up = QPushButton("上移", self)
        b_dn = QPushButton("下移", self)
        b_add.clicked.connect(self._add_step)
        b_rm.clicked.connect(self._remove_step)
        b_up.clicked.connect(self._move_up)
        b_dn.clicked.connect(self._move_down)
        row_btns.addWidget(b_add)
        row_btns.addWidget(b_rm)
        row_btns.addWidget(b_up)
        row_btns.addWidget(b_dn)
        left.addLayout(row_btns)
        root.addLayout(left, stretch=1)

        detail = QGroupBox("步骤属性", self)
        form = QFormLayout(detail)
        self._phase = QComboBox(detail)
        for p in BusinessPhase:
            self._phase.addItem(business_phase_label(p), p)
        self._duration = QSpinBox(detail)
        self._duration.setRange(1, 86400)
        self._duration.setSuffix(" s")
        self._override = QComboBox(detail)
        self._override.setEditable(True)
        self._override.lineEdit().setPlaceholderText("可选：覆盖状态栏显示")
        form.addRow("业务阶段", self._phase)
        form.addRow("计划时长", self._duration)
        form.addRow("显示覆盖", self._override)

        apply_btn = QPushButton("应用到当前行", detail)
        apply_btn.clicked.connect(self._apply_row)
        form.addRow(apply_btn)
        root.addWidget(detail, stretch=1)

        self._phase.currentIndexChanged.connect(self._maybe_apply_dirty)
        self._duration.valueChanged.connect(self._maybe_apply_dirty)
        self._override.currentTextChanged.connect(self._maybe_apply_dirty)

    def _current_row(self) -> int:
        idx = self._list.currentIndex()
        return idx.row() if idx.isValid() else -1

    def _on_row_changed(self, current, _previous) -> None:
        self._syncing = True
        try:
            row = current.row()
            if row < 0 or row >= self._model.rowCount():
                return
            step = self._model.steps_snapshot()[row]
            ix = self._phase.findData(step.business_phase)
            if ix >= 0:
                self._phase.setCurrentIndex(ix)
            self._duration.setValue(step.plan_duration_sec)
            self._override.setCurrentText(step.display_override)
        finally:
            self._syncing = False

    def _maybe_apply_dirty(self) -> None:
        if self._syncing:
            return

    def _apply_row(self) -> None:
        row = self._current_row()
        if row < 0:
            QMessageBox.information(self, "方法编辑", "请先选择一行步骤。")
            return
        phase = self._phase.currentData()
        assert isinstance(phase, BusinessPhase)
        cur = self._model.steps_snapshot()[row]
        st = RecipeStep(
            step_uid=cur.step_uid,
            order_index=row,
            business_phase=phase,
            plan_duration_sec=int(self._duration.value()),
            device_args=dict(cur.device_args),
            display_override=self._override.currentText().strip(),
        )
        self._model.replace_at(row, st)

    def _add_step(self) -> None:
        self._model.append_new_step()
        last = self._model.rowCount() - 1
        self._list.setCurrentIndex(self._model.index(last, 0))

    def _remove_step(self) -> None:
        rows = [i.row() for i in self._list.selectionModel().selectedIndexes()]
        if not rows:
            r = self._current_row()
            if r >= 0:
                rows = [r]
        if not rows:
            return
        if self._model.rowCount() <= 1:
            QMessageBox.warning(self, "方法编辑", "至少保留一个步骤。")
            return
        self._model.remove_rows(rows)

    def _move_up(self) -> None:
        r = self._current_row()
        if r < 0:
            return
        self._model.move_up(r)
        self._list.setCurrentIndex(self._model.index(r - 1, 0))

    def _move_down(self) -> None:
        r = self._current_row()
        if r < 0:
            return
        self._model.move_down(r)
        self._list.setCurrentIndex(self._model.index(r + 1, 0))
