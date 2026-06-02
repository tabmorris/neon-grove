from __future__ import annotations

import pygame

from game.effects import ease_out_cubic, lerp_color, pulse
from game.game_state import GameState
from game.particles import ParticleSystem
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
        self.particles = ParticleSystem(screen.get_size())
        self.vignette = self._build_vignette(screen.get_size())

    def draw(self, game_state: GameState, delta_seconds: float) -> None:
        self.elapsed_seconds += delta_seconds
        self._sync_feedback(game_state)
        self.particles.update(delta_seconds)

        self._draw_background()
        self.particles.draw_ambient(self.screen, self.elapsed_seconds)
        self._draw_food(game_state)
        self._draw_snake(game_state)
        self.particles.draw_feedback(self.screen)
        self._draw_collection_flash(game_state)
        self.ui.draw_score(self.screen, game_state.score)

        if game_state.play_state == PlayState.TITLE:
            self._draw_overlay_tint()
            self.ui.draw_title(self.screen)
        elif game_state.play_state == PlayState.PAUSED:
            self._draw_overlay_tint()
            self.ui.draw_pause(self.screen)
        elif game_state.play_state == PlayState.GAME_OVER:
            self._draw_overlay_tint()
            self.ui.draw_game_over(self.screen, game_state.score)

        pygame.display.flip()

    def _sync_feedback(self, game_state: GameState) -> None:
        collection_cell = game_state.consume_collection_cell()
        if collection_cell is None:
            return

        x, y = grid_to_pixel(collection_cell, CELL_SIZE)
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        self.particles.emit_food_burst(center)

    def _draw_background(self) -> None:
        width, height = self.screen.get_size()
        for y in range(height):
            amount = y / max(1, height - 1)
            color = lerp_color(colors.BACKGROUND, colors.BACKGROUND_MID, amount * 0.7)
            pygame.draw.line(self.screen, color, (0, y), (width, y))

        self._draw_glow_patch((width * 0.18, height * 0.26), colors.SNAKE_GLOW, 128, 22)
        self._draw_glow_patch((width * 0.79, height * 0.71), colors.FOOD_GLOW, 180, 18)
        self._draw_glow_patch((width * 0.55, height * 0.18), colors.MAGENTA_ACCENT, 140, 12)

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

        self.screen.blit(self.vignette, (0, 0))

    def _draw_glow_patch(
        self,
        center: tuple[float, float],
        color: tuple[int, int, int],
        radius: int,
        alpha: int,
    ) -> None:
        patch = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for step in range(5, 0, -1):
            step_radius = int(radius * step / 5)
            step_alpha = max(2, int(alpha * (1 - step / 6)))
            pygame.draw.circle(patch, (*color, step_alpha), (radius, radius), step_radius)
        self.screen.blit(patch, (center[0] - radius, center[1] - radius))

    def _draw_snake(self, game_state: GameState) -> None:
        for index, cell in enumerate(reversed(game_state.snake.body)):
            x, y = grid_to_pixel(cell, CELL_SIZE)
            inset = 3 if index % 2 else 2
            rect = pygame.Rect(x + inset, y + inset, CELL_SIZE - inset * 2, CELL_SIZE - inset * 2)
            is_head = index == len(game_state.snake.body) - 1
            color = colors.SNAKE_HEAD if is_head else colors.SNAKE_BODY

            if not is_head:
                fade = 0.7 + (index / max(1, len(game_state.snake.body))) * 0.3
                color = tuple(int(channel * fade) for channel in color)

            center = rect.center
            draw_glow_circle(self.screen, center, colors.SNAKE_GLOW, CELL_SIZE // 3, layers=3 if is_head else 2)
            if not is_head:
                trail_rect = rect.inflate(-8, -8)
                pygame.draw.rect(self.screen, colors.SNAKE_TRAIL, trail_rect, border_radius=5)
            pygame.draw.rect(self.screen, color, rect, border_radius=7)
            pygame.draw.rect(self.screen, (*colors.TEXT_GLOW,), rect.inflate(-8, -8), 1, border_radius=5)

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
        bob = int(2 * pulse(self.elapsed_seconds, speed=5.0, low=-1.0, high=1.0))
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2 + bob)
        radius = int((CELL_SIZE // 3) * pulse(self.elapsed_seconds, speed=4.0, low=0.85, high=1.2))

        draw_glow_circle(self.screen, center, colors.FOOD_GLOW, radius, layers=5)
        pygame.draw.circle(self.screen, colors.FOOD, center, radius)
        pygame.draw.circle(self.screen, colors.FOOD_CORE, center, max(2, radius // 2))
        sparkle_offset = int(8 * pulse(self.elapsed_seconds, speed=3.4, low=-0.8, high=0.8))
        pygame.draw.circle(self.screen, colors.MAGENTA_ACCENT, (center[0] + sparkle_offset, center[1] - 10), 2)

    def _draw_collection_flash(self, game_state: GameState) -> None:
        if game_state.collection_flash <= 0:
            return
        amount = ease_out_cubic(game_state.collection_flash / 0.22)
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((*colors.FLASH, int(24 * amount)))
        self.screen.blit(overlay, (0, 0))

    def _draw_overlay_tint(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 8, 10, 96))
        self.screen.blit(overlay, (0, 0))

    def _build_vignette(self, size: tuple[int, int]) -> pygame.Surface:
        width, height = size
        vignette = pygame.Surface(size, pygame.SRCALPHA)
        center = pygame.Vector2(width / 2, height / 2)
        max_distance = center.length()
        for y in range(0, height, 6):
            for x in range(0, width, 6):
                distance = pygame.Vector2(x - center.x, y - center.y).length()
                alpha = int(max(0, (distance / max_distance - 0.42)) * 130)
                pygame.draw.rect(vignette, (*colors.VIGNETTE, alpha), (x, y, 6, 6))
        return vignette
