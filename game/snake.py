from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from settings import GRID_HEIGHT, GRID_WIDTH, START_LENGTH
from utils.constants import DIRECTION_RIGHT, OPPOSITE_DIRECTIONS


@dataclass
class Snake:
    body: deque[tuple[int, int]] = field(default_factory=deque)
    direction: tuple[int, int] = DIRECTION_RIGHT
    pending_direction: tuple[int, int] = DIRECTION_RIGHT
    grow_pending: int = 0

    @classmethod
    def centered(cls) -> "Snake":
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        body = deque((center_x - index, center_y) for index in range(START_LENGTH))
        return cls(body=body)

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    def queue_direction(self, direction: tuple[int, int]) -> None:
        if direction == OPPOSITE_DIRECTIONS[self.direction]:
            return
        self.pending_direction = direction

    def move(self) -> tuple[int, int]:
        if self.pending_direction != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = self.pending_direction

        head_x, head_y = self.head
        next_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.appendleft(next_head)

        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return next_head

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def hit_wall(self) -> bool:
        head_x, head_y = self.head
        return head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT

    def hit_self(self) -> bool:
        return self.head in list(self.body)[1:]

    def occupies(self) -> set[tuple[int, int]]:
        return set(self.body)
