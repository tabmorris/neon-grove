from __future__ import annotations

import pygame

from game.atmosphere_renderer import AtmosphereRenderer
from game.effects import ease_out_cubic, pulse
from game.game_state import GameState
from game.particles import ParticleSystem
from game.ui import UI
from settings import CELL_SIZE
from utils import colors
from utils.constants import PlayState
from utils.helpers import draw_glow_circle, grid_to_pixel


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.ui = UI()
        self.elapsed_seconds = 0.0
        self.particles = ParticleSystem(screen.get_size())
        self.atmosphere = AtmosphereRenderer(screen.get_size())
        self.snake_glow_cache: dict[tuple[int, int, int, int], pygame.Surface] = {}

    def draw(self, game_state: GameState, delta_seconds: float) -> None:
        self.elapsed_seconds += delta_seconds
        self._sync_feedback(game_state)
        self.particles.update(delta_seconds)

        self.atmosphere.draw(self.screen)
        self.particles.draw_ambient(self.screen, self.elapsed_seconds)

        if game_state.play_state != PlayState.TITLE:
            self._draw_collection_flash(game_state)
            self._draw_food(game_state)
            self._draw_snake(game_state)
            self.particles.draw_feedback(self.screen)
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

    def _draw_snake(self, game_state: GameState) -> None:
        for index, cell in enumerate(reversed(game_state.snake.body)):
            x, y = grid_to_pixel(cell, CELL_SIZE)
            inset = 2
            rect = pygame.Rect(x + inset, y + inset, CELL_SIZE - inset * 2, CELL_SIZE - inset * 2)
            is_head = index == len(game_state.snake.body) - 1
            color = colors.SNAKE_HEAD if is_head else colors.SNAKE_BODY

            if not is_head:
                fade = 0.7 + (index / max(1, len(game_state.snake.body))) * 0.3
                color = tuple(int(channel * fade) for channel in color)

            self._draw_snake_glow(rect, is_head)
            pygame.draw.rect(self.screen, color, rect, border_radius=7)

            if is_head:
                self._draw_eyes(rect, game_state.snake.direction)

    def _draw_snake_glow(self, rect: pygame.Rect, is_head: bool) -> None:
        padding = 8 if is_head else 6
        alpha = 64 if is_head else 42
        cache_key = (rect.width, rect.height, padding, alpha)
        glow_surface = self.snake_glow_cache.get(cache_key)

        if glow_surface is None:
            glow_rect = pygame.Rect(0, 0, rect.width + padding * 2, rect.height + padding * 2)
            glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            for layer in range(3, 0, -1):
                layer_padding = layer * 2
                layer_rect = glow_rect.inflate(-layer_padding, -layer_padding)
                layer_alpha = max(12, alpha // layer)
                pygame.draw.rect(
                    glow_surface,
                    (*colors.SNAKE_GLOW, layer_alpha),
                    layer_rect,
                    border_radius=9,
                )
            self.snake_glow_cache[cache_key] = glow_surface

        self.screen.blit(glow_surface, (rect.x - padding, rect.y - padding))

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
        radius = int((CELL_SIZE // 3) * pulse(self.elapsed_seconds, speed=3.0, low=0.9, high=1.05))

        draw_glow_circle(self.screen, center, colors.FOOD_GLOW, radius, layers=3)
        pygame.draw.circle(self.screen, colors.FOOD, center, radius)
        pygame.draw.circle(self.screen, colors.FOOD_CORE, center, max(2, radius // 2))
        sparkle_offset = int(5 * pulse(self.elapsed_seconds, speed=2.4, low=-0.8, high=0.8))
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
