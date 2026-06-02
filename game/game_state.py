from __future__ import annotations

from dataclasses import dataclass, field

from game.food import Food
from game.snake import Snake
from settings import MIN_MOVE_INTERVAL, SPEEDUP_PER_FOOD, STARTING_MOVE_INTERVAL
from utils.constants import PlayState


@dataclass
class GameState:
    snake: Snake = field(default_factory=Snake.centered)
    food: Food = field(init=False)
    play_state: PlayState = PlayState.START
    score: int = 0
    move_interval: float = STARTING_MOVE_INTERVAL
    move_timer: float = 0

    def __post_init__(self) -> None:
        self.food = Food.spawn(self.snake.occupies())

    def start(self) -> None:
        if self.play_state == PlayState.START:
            self.play_state = PlayState.PLAYING
        elif self.play_state == PlayState.GAME_OVER:
            self.reset()
            self.play_state = PlayState.PLAYING

    def reset(self) -> None:
        self.snake = Snake.centered()
        self.food = Food.spawn(self.snake.occupies())
        self.score = 0
        self.move_interval = STARTING_MOVE_INTERVAL
        self.move_timer = 0
        self.play_state = PlayState.START

    def update(self, delta_seconds: float) -> None:
        if self.play_state != PlayState.PLAYING:
            return

        self.move_timer += delta_seconds
        while self.move_timer >= self.move_interval and self.play_state == PlayState.PLAYING:
            self.move_timer -= self.move_interval
            self._step()

    def _step(self) -> None:
        self.snake.move()

        if self.snake.hit_wall() or self.snake.hit_self():
            self.play_state = PlayState.GAME_OVER
            return

        if self.snake.head == self.food.position:
            self.score += 1
            self.snake.grow()
            self.move_interval = max(
                MIN_MOVE_INTERVAL,
                self.move_interval - SPEEDUP_PER_FOOD,
            )
            self.food = Food.spawn(self.snake.occupies())
