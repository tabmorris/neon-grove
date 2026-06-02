from __future__ import annotations

import pygame

from game.effects import pulse
from game.game_state import GameState
from game.ui import UI
from settings import CELL_SIZE, GRID_HEIGHT, GRID_WIDTH
from utils import colors
from utils.constants import PlayState
from utils.helpers import draw_glow_circle, grid_to_pixel


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.ui = UI()
        self.elapsed_seconds = 0.0

    def draw(self, game_state: GameState) -> None:
        self.elapsed_seconds += 1 / 60
        self._draw_background()
        self._draw_food(game_state)
        self._draw_snake(game_state)
        self.ui.draw_score(self.screen, game_state.score)

        if game_state.play_state == PlayState.START:
            self.ui.draw_center_message(
                self.screen,
                "Neon Grove",
                "Press Space or move to begin",
            )
        elif game_state.play_state == PlayState.GAME_OVER:
            self.ui.draw_center_message(
                self.screen,
                "Game Over",
                "Press Space or Enter to restart",
                colors.WARNING,
            )

        pygame.display.flip()

    def _draw_background(self) -> None:
        self.screen.fill(colors.BACKGROUND)
        width, height = self.screen.get_size()

        pygame.draw.rect(self.screen, colors.CANOPY, (0, 0, width, height), 0)

        for y in range(0, height, CELL_SIZE):
            line_color = colors.BACKGROUND_GRID if y % (CELL_SIZE * 5) == 0 else (10, 29, 31)
            pygame.draw.line(self.screen, line_color, (0, y), (width, y), 1)

        for x in range(0, width, CELL_SIZE):
            line_color = colors.BACKGROUND_GRID if x % (CELL_SIZE * 5) == 0 else (10, 29, 31)
            pygame.draw.line(self.screen, line_color, (x, 0), (x, height), 1)

        for index in range(9):
            x = 100 + index * 151
            y = 95 + (index % 4) * 137
            radius = 2 + index % 3
            glow = pulse(self.elapsed_seconds + index, speed=1.6, low=0.45, high=1.0)
            color = tuple(int(channel * glow) for channel in colors.FOOD_GLOW)
            draw_glow_circle(self.screen, (x % width, y % height), color, radius, layers=2)

    def _draw_snake(self, game_state: GameState) -> None:
        for index, cell in enumerate(reversed(game_state.snake.body)):
            x, y = grid_to_pixel(cell, CELL_SIZE)
            rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
            is_head = index == len(game_state.snake.body) - 1
            color = colors.SNAKE_HEAD if is_head else colors.SNAKE_BODY

            if not is_head:
                fade = 0.7 + (index / max(1, len(game_state.snake.body))) * 0.3
                color = tuple(int(channel * fade) for channel in color)

            center = rect.center
            draw_glow_circle(self.screen, center, colors.SNAKE_GLOW, CELL_SIZE // 3, layers=2)
            pygame.draw.rect(self.screen, color, rect, border_radius=7)

            if is_head:
                self._draw_eyes(rect, game_state.snake.direction)

    def _draw_eyes(self, head_rect: pygame.Rect, direction: tuple[int, int]) -> None:
        center_x, center_y = head_rect.center
        offset_x = direction[0] * 4
        offset_y = direction[1] * 4

        if direction[0] != 0:
            eye_positions = [
                (center_x + offset_x, center_y - 5),
                (center_x + offset_x, center_y + 5),
            ]
        else:
            eye_positions = [
                (center_x - 5, center_y + offset_y),
                (center_x + 5, center_y + offset_y),
            ]

        for position in eye_positions:
            pygame.draw.circle(self.screen, colors.BACKGROUND, position, 2)

    def _draw_food(self, game_state: GameState) -> None:
        if game_state.food.position == (-1, -1):
            return

        x, y = grid_to_pixel(game_state.food.position, CELL_SIZE)
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        radius = int((CELL_SIZE // 3) * pulse(self.elapsed_seconds, speed=4.0, low=0.85, high=1.2))

        draw_glow_circle(self.screen, center, colors.FOOD_GLOW, radius, layers=5)
        pygame.draw.circle(self.screen, colors.FOOD, center, radius)
        pygame.draw.circle(self.screen, colors.FOOD_CORE, center, max(2, radius // 2))
