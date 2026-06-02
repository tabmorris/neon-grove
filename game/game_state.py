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
    play_state: PlayState = PlayState.TITLE
    score: int = 0
    move_interval: float = STARTING_MOVE_INTERVAL
    move_timer: float = 0
    collection_cell: tuple[int, int] | None = None
    collection_flash: float = 0.0

    def __post_init__(self) -> None:
        self.food = Food.spawn(self.snake.occupies())

    def start(self) -> None:
        if self.play_state == PlayState.TITLE:
            self.play_state = PlayState.PLAYING
        elif self.play_state == PlayState.GAME_OVER:
            self.reset()
            self.play_state = PlayState.PLAYING
        elif self.play_state == PlayState.PAUSED:
            self.play_state = PlayState.PLAYING

    def toggle_pause(self) -> None:
        if self.play_state == PlayState.PLAYING:
            self.play_state = PlayState.PAUSED
        elif self.play_state == PlayState.PAUSED:
            self.play_state = PlayState.PLAYING

    def reset(self) -> None:
        self.snake = Snake.centered()
        self.food = Food.spawn(self.snake.occupies())
        self.score = 0
        self.move_interval = STARTING_MOVE_INTERVAL
        self.move_timer = 0
        self.collection_cell = None
        self.collection_flash = 0.0
        self.play_state = PlayState.TITLE

    def consume_collection_cell(self) -> tuple[int, int] | None:
        cell = self.collection_cell
        self.collection_cell = None
        return cell

    def update(self, delta_seconds: float) -> None:
        self.collection_flash = max(0.0, self.collection_flash - delta_seconds)

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
            self.collection_cell = self.food.position
            self.collection_flash = 0.22
            self.score += 1
            self.snake.grow()
            self.move_interval = max(
                MIN_MOVE_INTERVAL,
                self.move_interval - SPEEDUP_PER_FOOD,
            )
            self.food = Food.spawn(self.snake.occupies())
