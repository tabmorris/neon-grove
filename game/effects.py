from __future__ import annotations

import math


def pulse(elapsed_seconds: float, speed: float = 2.0, low: float = 0.75, high: float = 1.0) -> float:
    wave = (math.sin(elapsed_seconds * speed) + 1) / 2
    return low + (high - low) * wave


def ease_out_cubic(value: float) -> float:
    clamped = max(0.0, min(1.0, value))
    return 1 - pow(1 - clamped, 3)


def lerp_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    clamped = max(0.0, min(1.0, amount))
    return tuple(int(a + (b - a) * clamped) for a, b in zip(start, end))
