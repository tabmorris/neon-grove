from __future__ import annotations

import random
from dataclasses import dataclass

from settings import GRID_HEIGHT, GRID_WIDTH


@dataclass
class Food:
    position: tuple[int, int]

    @classmethod
    def spawn(cls, blocked_cells: set[tuple[int, int]]) -> "Food":
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in blocked_cells
        ]
        if not available:
            return cls((-1, -1))
        return cls(random.choice(available))
