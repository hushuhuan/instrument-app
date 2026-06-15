from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from instrument_app.app.application_context import ApplicationContext
from instrument_app.domain.selftest.self_test_orchestrator import (
    SelfTestStepId,
    run_self_test,
    step_title,
)
from instrument_app.logging.log import append_selftest_report_json

_STATUS_CN = {
    "passed": "通过",
    "failed": "失败",
    "not_run": "未执行",
}


class _SelfTestWorker(QThread):
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, ctx: ApplicationContext) -> None:
        super().__init__()
        self._ctx = ctx

    def run(self) -> None:
        try:
            report = run_self_test(self._ctx.config, self._ctx.hal)
            self.finished_ok.emit(report)
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


class SelfTestDialog(QDialog):
    """Shows fixed-order self-test results; runs work on a background thread."""

    def __init__(
        self,
        ctx: ApplicationContext,
        on_active_changed: Callable[[], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._on_active_changed = on_active_changed
        self.setWindowTitle("仪器自检")
        self.setMinimumSize(720, 400)

        self._ctx.run_coordinator.set_self_test_active(True)
        self._notify_parent()

        root = QVBoxLayout(self)
        self._status = QLabel("自检执行中，请稍候…", self)
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        self._table = QTableWidget(0, 4, self)
        self._table.setHorizontalHeaderLabels(["步骤", "状态", "详情", "耗时 (ms)"])
        self._table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self._table, stretch=1)

        btn_row = QHBoxLayout()
        self._close_btn = QPushButton("关闭", self)
        self._close_btn.setEnabled(False)
        self._close_btn.clicked.connect(self.accept)
        btn_row.addStretch(1)
        btn_row.addWidget(self._close_btn)
        root.addLayout(btn_row)

        self._worker = _SelfTestWorker(ctx)
        self._worker.finished_ok.connect(self._on_report)
        self._worker.failed.connect(self._on_worker_failed)
        self._worker.start()

    def _notify_parent(self) -> None:
        self._on_active_changed()

    def _on_report(self, report: dict) -> None:
        append_selftest_report_json(report)
        overall = report.get("overallPass", False)
        self._status.setText(
            "自检完成：全部通过。" if overall else "自检完成：存在失败或未执行项，详见下表。"
        )
        items = report.get("items", [])
        self._table.setRowCount(len(items))
        id_to_title = {s.value: step_title(s) for s in SelfTestStepId}
        for row, it in enumerate(items):
            sid = str(it.get("stepId", ""))
            title = id_to_title.get(sid, sid)
            st = str(it.get("status", ""))
            msg = str(it.get("message", ""))
            ms = it.get("durationMs")
            self._table.setItem(row, 0, QTableWidgetItem(title))
            self._table.setItem(row, 1, QTableWidgetItem(_STATUS_CN.get(st, st)))
            self._table.setItem(row, 2, QTableWidgetItem(msg))
            dur = "" if ms is None else str(ms)
            self._table.setItem(row, 3, QTableWidgetItem(dur))
            for c in range(4):
                item = self._table.item(row, c)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._close_btn.setEnabled(True)

    def _on_worker_failed(self, err: str) -> None:
        QMessageBox.critical(self, "自检异常", err)
        self._status.setText("自检执行失败。")
        self._close_btn.setEnabled(True)

    def closeEvent(self, event) -> None:
        if self._worker.isRunning():
            event.ignore()
            return
        self._ctx.run_coordinator.set_self_test_active(False)
        self._notify_parent()
        super().closeEvent(event)

    def reject(self) -> None:
        if self._worker.isRunning():
            return
        self._ctx.run_coordinator.set_self_test_active(False)
        self._notify_parent()
        super().reject()

    def accept(self) -> None:
        self._ctx.run_coordinator.set_self_test_active(False)
        self._notify_parent()
        super().accept()
