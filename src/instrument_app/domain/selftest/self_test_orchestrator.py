from __future__ import annotations

import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

from instrument_app.domain.app_config import AppConfig
from instrument_app.domain.selftest.disk_check import check_disk_space
from instrument_app.domain.selftest.network_check import check_network
from instrument_app.hal.interfaces.instrument_hal import InstrumentHal


class SelfTestStepId(str, Enum):
    NETWORK = "Network"
    DISK_SPACE = "DiskSpace"
    PUMP_INIT = "PumpInit"
    ROTARY_VALVE_INIT = "RotaryValveInit"
    STEPPER_HOME = "StepperHome"
    CHILLER_COMM = "ChillerComm"


_STEP_ORDER: list[SelfTestStepId] = [
    SelfTestStepId.NETWORK,
    SelfTestStepId.DISK_SPACE,
    SelfTestStepId.PUMP_INIT,
    SelfTestStepId.ROTARY_VALVE_INIT,
    SelfTestStepId.STEPPER_HOME,
    SelfTestStepId.CHILLER_COMM,
]


def step_title(step: SelfTestStepId) -> str:
    return {
        SelfTestStepId.NETWORK: "网络",
        SelfTestStepId.DISK_SPACE: "磁盘空间",
        SelfTestStepId.PUMP_INIT: "泵初始化",
        SelfTestStepId.ROTARY_VALVE_INIT: "旋转阀初始化",
        SelfTestStepId.STEPPER_HOME: "步进回零",
        SelfTestStepId.CHILLER_COMM: "冷机通讯",
    }.get(step, step.value)


def _not_run(step: SelfTestStepId) -> dict[str, Any]:
    return {
        "stepId": step.value,
        "status": "not_run",
        "message": "未执行（前置步骤失败）",
    }


def run_self_test(cfg: AppConfig, hal: InstrumentHal) -> dict[str, Any]:
    """Execute six fixed self-test steps; build a dict matching self-test-report.schema.json."""
    run_id = str(uuid4())
    started = datetime.now(timezone.utc)
    items: list[dict[str, Any]] = []
    failed = False

    hal_ops: dict[SelfTestStepId, Callable[[], tuple[bool, str]]] = {
        SelfTestStepId.PUMP_INIT: hal.init_pumps,
        SelfTestStepId.ROTARY_VALVE_INIT: hal.init_rotary_valve,
        SelfTestStepId.STEPPER_HOME: hal.home_stepper,
        SelfTestStepId.CHILLER_COMM: hal.chiller_handshake,
    }

    for step in _STEP_ORDER:
        if failed:
            items.append(_not_run(step))
            continue

        t0 = time.perf_counter()
        ok = False
        msg = ""
        try:
            if step == SelfTestStepId.NETWORK:
                ok, msg = check_network(cfg)
            elif step == SelfTestStepId.DISK_SPACE:
                ok, msg = check_disk_space(cfg)
            else:
                ok, msg = hal_ops[step]()
        except Exception as e:  # noqa: BLE001 — surface as step failure
            ok = False
            msg = str(e)
        duration_ms = int((time.perf_counter() - t0) * 1000)

        if ok:
            items.append(
                {
                    "stepId": step.value,
                    "status": "passed",
                    "message": msg,
                    "durationMs": duration_ms,
                }
            )
        else:
            items.append(
                {
                    "stepId": step.value,
                    "status": "failed",
                    "message": msg,
                    "durationMs": duration_ms,
                }
            )
            failed = True

    ended = datetime.now(timezone.utc)
    overall_pass = all(it["status"] == "passed" for it in items)
    return {
        "schemaVersion": 1,
        "runId": run_id,
        "startedAt": _iso_z(started),
        "endedAt": _iso_z(ended),
        "overallPass": overall_pass,
        "items": items,
    }


def _iso_z(dt: datetime) -> str:
    s = dt.isoformat(timespec="milliseconds")
    if s.endswith("+00:00"):
        return s[:-6] + "Z"
    return s
