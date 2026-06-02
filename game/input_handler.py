from __future__ import annotations

import pygame

from game.game_state import GameState
from utils.constants import (
    DIRECTION_DOWN,
    DIRECTION_LEFT,
    DIRECTION_RIGHT,
    DIRECTION_UP,
    PlayState,
)


class InputHandler:
    def __init__(self) -> None:
        self.direction_keys = {
            pygame.K_UP: DIRECTION_UP,
            pygame.K_w: DIRECTION_UP,
            pygame.K_DOWN: DIRECTION_DOWN,
            pygame.K_s: DIRECTION_DOWN,
            pygame.K_LEFT: DIRECTION_LEFT,
            pygame.K_a: DIRECTION_LEFT,
            pygame.K_RIGHT: DIRECTION_RIGHT,
            pygame.K_d: DIRECTION_RIGHT,
        }

    def handle_event(self, event: pygame.event.Event, game_state: GameState) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
            game_state.start()
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        direction = self.direction_keys.get(event.key)
        if direction is not None:
            game_state.snake.queue_direction(direction)
            if game_state.play_state == PlayState.START:
                game_state.start()
