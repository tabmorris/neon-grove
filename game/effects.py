from __future__ import annotations

import math


def pulse(elapsed_seconds: float, speed: float = 2.0, low: float = 0.75, high: float = 1.0) -> float:
    wave = (math.sin(elapsed_seconds * speed) + 1) / 2
    return low + (high - low) * wave
