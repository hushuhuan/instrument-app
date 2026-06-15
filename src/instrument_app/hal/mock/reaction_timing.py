from __future__ import annotations


def mock_reaction_step_ms(
    plan_duration_sec: int,
    mock_time_scale_divisor: int,
    default_scale: int,
) -> int:
    div = mock_time_scale_divisor if mock_time_scale_divisor > 0 else default_scale
    ms = (plan_duration_sec * 1000) // max(1, div)
    return max(250, ms)
