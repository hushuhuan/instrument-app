from __future__ import annotations

import json

from instrument_app.logging.alarm_log import append_alarm, alarm_log_file


def test_append_alarm_writes_json_line(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    append_alarm("t_code", "hello", severity="error")
    path = alarm_log_file()
    assert path.is_file()
    line = path.read_text(encoding="utf-8").strip()
    obj = json.loads(line)
    assert obj["code"] == "t_code"
    assert obj["message"] == "hello"
    assert obj["severity"] == "error"
