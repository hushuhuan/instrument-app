from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from instrument_app.app.application_context import ApplicationContext
from instrument_app.logging.debug_device import append_debug_device_log


class DebugDevicePage(QWidget):
    """Manual bench controls for pump / rotary valve / chiller (HAL debug API v1)."""

    def __init__(self, ctx: ApplicationContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._interactive: list[QWidget] = []

        root = QVBoxLayout(self)
        self._block_reason = QLabel("", self)
        self._block_reason.setWordWrap(True)
        self._block_reason.setStyleSheet("color:#b00020;font-weight:600;")
        root.addWidget(self._block_reason)

        pump_box = QGroupBox("注射泵", self)
        pump_l = QFormLayout(pump_box)
        self._flow = QDoubleSpinBox(pump_box)
        self._flow.setRange(0.1, 10_000.0)
        self._flow.setDecimals(2)
        self._flow.setSuffix(" µL/min")
        self._flow.setValue(100.0)
        pump_l.addRow("流速", self._flow)
        row_p = QHBoxLayout()
        b_prime = QPushButton("灌注", pump_box)
        b_disp = QPushButton("分配", pump_box)
        b_stop = QPushButton("停止", pump_box)
        b_prime.clicked.connect(lambda: self._pump("prime"))
        b_disp.clicked.connect(lambda: self._pump("dispense"))
        b_stop.clicked.connect(lambda: self._pump("stop"))
        row_p.addWidget(b_prime)
        row_p.addWidget(b_disp)
        row_p.addWidget(b_stop)
        pump_l.addRow(row_p)
        self._interactive.extend([self._flow, b_prime, b_disp, b_stop])

        valve_box = QGroupBox("旋转阀", self)
        valve_l = QHBoxLayout(valve_box)
        self._channel = QSpinBox(valve_box)
        self._channel.setRange(0, 15)
        b_go = QPushButton("转到通道", valve_box)
        b_go.clicked.connect(self._valve_goto)
        valve_l.addWidget(QLabel("通道 (0–15)", valve_box))
        valve_l.addWidget(self._channel)
        valve_l.addWidget(b_go)
        self._interactive.extend([self._channel, b_go])

        chiller_box = QGroupBox("温控仪", self)
        ch_l = QFormLayout(chiller_box)
        self._setpoint = QDoubleSpinBox(chiller_box)
        self._setpoint.setRange(-40.0, 150.0)
        self._setpoint.setDecimals(1)
        self._setpoint.setSuffix(" °C")
        self._setpoint.setValue(25.0)
        ch_row = QHBoxLayout()
        b_set = QPushButton("写入设定", chiller_box)
        b_read = QPushButton("读取设定", chiller_box)
        b_set.clicked.connect(self._chiller_set)
        b_read.clicked.connect(self._chiller_read)
        ch_row.addWidget(b_set)
        ch_row.addWidget(b_read)
        ch_l.addRow("温度设定", self._setpoint)
        ch_l.addRow(ch_row)
        self._interactive.extend([self._setpoint, b_set, b_read])

        self._last = QLabel("—", self)
        self._last.setWordWrap(True)
        self._last.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        root.addWidget(pump_box)
        root.addWidget(valve_box)
        root.addWidget(chiller_box)
        root.addWidget(QLabel("最近一次结果：", self))
        root.addWidget(self._last)
        root.addStretch(1)

        self._set_tooltips()
        rc = self._ctx.run_coordinator
        rc.run_phase_changed.connect(lambda _p: self._refresh_availability())
        rc.run_finished.connect(lambda _p: self._refresh_availability())
        self._refresh_availability()

    def _set_tooltips(self) -> None:
        tip = (
            "仅在运行空闲且未进行自检时可用。运行中或自检中会禁用，避免与工艺/自检互锁冲突（FR-016 相关）。"
        )
        for w in self._interactive:
            w.setToolTip(tip)
        self.setToolTip(tip)

    def _allowed(self) -> tuple[bool, str]:
        rc = self._ctx.run_coordinator
        if rc.self_test_active:
            return False, "自检进行中，设备调试已禁用。"
        if not rc.is_idle():
            return False, "运行未空闲，设备调试已禁用（请等待当前运行结束）。"
        return True, ""

    def _refresh_availability(self) -> None:
        ok, reason = self._allowed()
        self._block_reason.setText("" if ok else reason)
        for w in self._interactive:
            w.setEnabled(ok)

    def _audit(self, summary: str) -> None:
        append_debug_device_log(summary)

    def _pump(self, action: str) -> None:
        ok_gate, _ = self._allowed()
        if not ok_gate:
            return
        flow = float(self._flow.value())
        success, msg = self._ctx.hal.debug_pump_command(action, flow)
        self._last.setText(msg)
        self._audit(f"pump action={action} flow_ul_per_min={flow} ok={success} msg={msg}")
        if not success:
            QMessageBox.warning(self, "注射泵", msg)

    def _valve_goto(self) -> None:
        ok_gate, _ = self._allowed()
        if not ok_gate:
            return
        ch = int(self._channel.value())
        success, msg = self._ctx.hal.debug_rotary_valve_goto_channel(ch)
        self._last.setText(msg)
        self._audit(f"rotary_valve channel={ch} ok={success} msg={msg}")
        if not success:
            QMessageBox.warning(self, "旋转阀", msg)

    def _chiller_set(self) -> None:
        ok_gate, _ = self._allowed()
        if not ok_gate:
            return
        sp = float(self._setpoint.value())
        success, msg = self._ctx.hal.debug_chiller_set_setpoint(sp)
        self._last.setText(msg)
        self._audit(f"chiller setpoint_set={sp} ok={success} msg={msg}")
        if not success:
            QMessageBox.warning(self, "温控仪", msg)

    def _chiller_read(self) -> None:
        ok_gate, _ = self._allowed()
        if not ok_gate:
            return
        val, msg = self._ctx.hal.debug_chiller_read_setpoint()
        self._last.setText(msg)
        self._audit(f"chiller readback value={val} msg={msg}")
