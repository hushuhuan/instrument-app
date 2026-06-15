from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from instrument_app.app.application_context import ApplicationContext
from instrument_app.domain.app_config import ApplicationRunMode
from instrument_app.domain.parameter_validation import validate_for_ready
from instrument_app.domain.recipe_models import ProcessParameters
from instrument_app.domain.recipe_factory import (
    recipe_from_editor_steps,
    recipe_from_reaction_task,
)
from instrument_app.persistence.recipe_repository import load_recipe_json, save_recipe_json
from instrument_app.ui.debug_device_page import DebugDevicePage
from instrument_app.ui.device_health_dialog import DeviceHealthDialog
from instrument_app.ui.parameters_form import ParametersForm
from instrument_app.ui.parameters_summary_widget import ParametersSummaryWidget
from instrument_app.ui.reaction_task_dialog import ReactionTaskDialog
from instrument_app.ui.recipe_editor_widget import RecipeEditorWidget
from instrument_app.ui.recipe_steps_model import RecipeStepsModel
from instrument_app.ui.run_progress_widget import RunProgressWidget
from instrument_app.ui.self_test_dialog import SelfTestDialog
from instrument_app.ui.status_bar_presenter import StatusBarPresenter


class MainWindow(QMainWindow):
    def __init__(self, ctx: ApplicationContext) -> None:
        super().__init__()
        self._ctx = ctx
        self.setWindowTitle("有机合成仪器控制")
        self.setMinimumSize(920, 640)

        if ctx.config.run_mode == ApplicationRunMode.MOCK:
            self._mock_banner = QLabel(
                "仿真模式 — 未连接真实硬件", self
            )
            self._mock_banner.setStyleSheet(
                "background:#fff3cd;color:#856404;padding:8px;font-weight:600;font-size:13px;"
            )
        else:
            self._mock_banner = None

        central = QWidget(self)
        v = QVBoxLayout(central)
        if self._mock_banner:
            v.addWidget(self._mock_banner)

        split = QSplitter(Qt.Orientation.Horizontal, central)

        left_panel = QWidget(split)
        left_lo = QVBoxLayout(left_panel)
        self._form = ParametersForm(left_panel)
        self._summary = ParametersSummaryWidget(left_panel)
        self._ready = QLabel(left_panel)
        self._ready.setWordWrap(True)
        left_lo.addWidget(self._form, stretch=2)
        left_lo.addWidget(self._summary, stretch=0)
        left_lo.addWidget(self._ready, stretch=0)

        right_panel = QWidget(split)
        right_lo = QVBoxLayout(right_panel)
        self._recipe_model = RecipeStepsModel(right_panel)
        self._recipe_model.append_new_step()
        self._recipe_editor = RecipeEditorWidget(self._recipe_model, right_panel)
        self._run_progress = RunProgressWidget(ctx.run_coordinator, right_panel)
        recipe_btns = QHBoxLayout()
        b_load = QPushButton("加载方法…", right_panel)
        b_save = QPushButton("保存方法…", right_panel)
        b_run = QPushButton("运行方法", right_panel)
        b_load.clicked.connect(self._on_load_recipe)
        b_save.clicked.connect(self._on_save_recipe)
        b_run.clicked.connect(self._on_run_recipe)
        recipe_btns.addWidget(b_load)
        recipe_btns.addWidget(b_save)
        recipe_btns.addWidget(b_run)
        right_lo.addWidget(self._recipe_editor, stretch=3)
        right_lo.addWidget(self._run_progress, stretch=0)
        right_lo.addLayout(recipe_btns)

        split.addWidget(left_panel)
        split.addWidget(right_panel)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 1)
        v.addWidget(split, stretch=1)
        self.setCentralWidget(central)

        dbg = QMenu("调试", self)
        act_export = QAction("导出状态栏快照…", self)
        act_export.triggered.connect(self._on_export_status_snapshot)
        dbg.addAction(act_export)
        dbg.addSeparator()
        act_health = QAction("设备健康", self)
        act_health.triggered.connect(self._on_device_health)
        dbg.addAction(act_health)
        dbg.addSeparator()
        act_dbg = QAction("设备调试", self)
        act_dbg.triggered.connect(self._on_debug_device)
        dbg.addAction(act_dbg)
        self.menuBar().addMenu(dbg)

        tb = QToolBar("主工具栏", self)
        tb.setMovable(False)
        act_self = QAction("自检", self)
        act_self.triggered.connect(self._on_self_test)
        tb.addAction(act_self)
        self._act_self_test = act_self
        act = QAction("反应任务", self)
        tb.addAction(act)
        act.triggered.connect(self._on_reaction_task)
        self.addToolBar(tb)

        self._status_presenter = StatusBarPresenter(
            ctx.hal, ctx.run_coordinator, self.statusBar(), self
        )

        self._form.parameters_edited.connect(self._on_parameters_edited)
        self._ctx.run_coordinator.run_finished.connect(self._on_run_finished)
        self._ctx.run_coordinator.run_phase_changed.connect(self._refresh_self_test_action)

        self._rebuild_validation()
        self._refresh_self_test_action()

    def _refresh_self_test_action(self, *_args: object) -> None:
        rc = self._ctx.run_coordinator
        can = rc.is_idle() and not rc.self_test_active
        self._act_self_test.setEnabled(can)
        if rc.self_test_active:
            self._act_self_test.setToolTip("自检会话进行中。")
        elif not rc.is_idle():
            self._act_self_test.setToolTip("运行中时无法自检（FR-016）。")
        else:
            self._act_self_test.setToolTip("")

    def _on_self_test(self) -> None:
        if not self._ctx.run_coordinator.is_idle():
            QMessageBox.warning(
                self, "无法自检", "当前有工艺运行或未空闲，无法启动自检。"
            )
            return
        if self._ctx.run_coordinator.self_test_active:
            return
        SelfTestDialog(self._ctx, self._refresh_self_test_action, self).exec()
        self._refresh_self_test_action()

    def _rebuild_validation(self) -> None:
        p = self._form.parameters()
        self._summary.set_parameters(p)
        err = validate_for_ready(p)
        if not err:
            self._ready.setText("参数校验：就绪，可提交反应任务或后续运行。")
            self._ready.setStyleSheet("color:#1b5e20;")
        else:
            self._ready.setText("参数校验：\n" + "\n".join(err))
            self._ready.setStyleSheet("color:#b00020;")

    def _on_parameters_edited(self) -> None:
        self._rebuild_validation()

    def _on_run_finished(self) -> None:
        self._rebuild_validation()
        self._refresh_self_test_action()

    def _on_load_recipe(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self, "加载方法", str(Path.cwd()), "JSON (*.json)"
        )
        if not path_str:
            return
        try:
            recipe = load_recipe_json(Path(path_str))
        except (OSError, ValueError, KeyError, TypeError) as e:
            QMessageBox.critical(self, "加载失败", str(e))
            return
        if not recipe.steps:
            QMessageBox.warning(self, "加载失败", "文件中没有有效步骤。")
            return
        self._form.set_parameters(recipe.parameters)
        self._recipe_model.set_steps(recipe.steps)
        self._rebuild_validation()

    def _on_save_recipe(self) -> None:
        err = validate_for_ready(self._form.parameters())
        if err:
            QMessageBox.warning(self, "参数未就绪", "\n".join(err))
            return
        steps = self._recipe_model.steps_snapshot()
        if not steps:
            QMessageBox.warning(self, "方法为空", "请至少保留一个步骤。")
            return
        path_str, _ = QFileDialog.getSaveFileName(
            self, "保存方法", str(Path.cwd()), "JSON (*.json)"
        )
        if not path_str:
            return
        path = Path(path_str)
        name = path.stem or "方法"
        recipe = recipe_from_editor_steps(name, self._form.parameters(), steps)
        try:
            save_recipe_json(path, recipe)
        except OSError as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _on_run_recipe(self) -> None:
        if self._ctx.config.run_mode != ApplicationRunMode.MOCK:
            QMessageBox.information(
                self,
                "提示",
                "当前为 Production 模式，真机 HAL 尚未接入。请使用 --mock 或 INSTRUMENT_USE_MOCK=1。",
            )
        if not self._ctx.run_coordinator.is_idle():
            QMessageBox.warning(
                self, "无法启动", "已有运行或会话未空闲，请先结束当前运行。"
            )
            return
        if self._ctx.run_coordinator.self_test_active:
            QMessageBox.warning(self, "无法启动", "自检进行中，无法启动工艺运行。")
            return
        err = validate_for_ready(self._form.parameters())
        if err:
            QMessageBox.warning(self, "参数未就绪", "\n".join(err))
            return
        steps = self._recipe_model.steps_snapshot()
        if not steps:
            QMessageBox.warning(self, "无法启动", "请至少编排一个步骤。")
            return
        recipe = recipe_from_editor_steps("主界面方法", self._form.parameters(), steps)
        self._ctx.run_coordinator.start_run(recipe)

    def _on_export_status_snapshot(self) -> None:
        data = self._status_presenter.export_snapshot_dict()
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "导出状态栏快照",
            str(Path.cwd()),
            "JSON (*.json)",
        )
        if not path_str:
            return
        try:
            Path(path_str).write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            QMessageBox.critical(self, "导出失败", str(e))

    def _on_device_health(self) -> None:
        DeviceHealthDialog(self._ctx, self).exec()

    def _on_debug_device(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("设备调试")
        dlg.setMinimumSize(520, 440)
        v = QVBoxLayout(dlg)
        v.addWidget(DebugDevicePage(self._ctx, dlg))
        dlg.exec()

    def _on_reaction_task(self) -> None:
        if self._ctx.config.run_mode != ApplicationRunMode.MOCK:
            QMessageBox.information(
                self,
                "提示",
                "当前为 Production 模式，真机 HAL 尚未接入。请使用 --mock 或 INSTRUMENT_USE_MOCK=1。",
            )
        if not self._ctx.run_coordinator.is_idle():
            QMessageBox.warning(
                self, "无法启动", "已有运行或会话未空闲，请先结束当前运行。"
            )
            return
        if self._ctx.run_coordinator.self_test_active:
            QMessageBox.warning(self, "无法启动", "自检进行中，无法启动工艺运行。")
            return
        base = self._form.parameters()
        dlg = ReactionTaskDialog(base, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        t = dlg.result_parameters()
        merged = ProcessParameters(
            reaction_time_sec=t.reaction_time_sec,
            stir_speed_rpm=t.stir_speed_rpm,
            reaction_temp_c=t.reaction_temp_c,
            rinse_params=base.rinse_params,
            solvent=base.solvent,
            extraction_params=base.extraction_params,
            filtration_params=base.filtration_params,
            sample_count=base.sample_count,
        )
        err = validate_for_ready(merged)
        if err:
            QMessageBox.warning(self, "参数未就绪", "\n".join(err))
            return
        recipe = recipe_from_reaction_task(merged)
        self._ctx.run_coordinator.start_run(recipe)
