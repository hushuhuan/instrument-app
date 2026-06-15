from __future__ import annotations

from instrument_app.logging.debug_device import append_debug_device_log, debug_device_log_file


def test_append_debug_device_log_writes(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    append_debug_device_log("pump prime ok=1")
    path = debug_device_log_file()
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "pump prime ok=1" in text
    assert "\t" in text
