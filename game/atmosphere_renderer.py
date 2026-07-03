from __future__ import annotations

import pygame

from game.effects import lerp_color
from settings import CELL_SIZE
from utils import colors


class AtmosphereRenderer:
    """Draws Neon Grove's cached, non-gameplay background atmosphere."""

    def __init__(self, size: tuple[int, int]) -> None:
        self.size = size
        self.background = pygame.Surface(size).convert()
        self.vignette = pygame.Surface(size, pygame.SRCALPHA)
        self._build_background()
        self._build_vignette()

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        surface.blit(self.vignette, (0, 0))

    def _build_background(self) -> None:
        width, height = self.size
        self._draw_gradient(width, height)
        self._draw_color_wash(width, height)
        self._draw_forest_floor_texture(width, height)
        self._draw_grid(width, height)

    def _draw_gradient(self, width: int, height: int) -> None:
        for y in range(height):
            amount = y / max(1, height - 1)
            upper = lerp_color(colors.BACKGROUND, colors.CANOPY, amount * 0.55)
            lower = lerp_color(colors.BACKGROUND_MID, colors.BACKGROUND, 1 - amount)
            color = lerp_color(upper, lower, amount * 0.32)
            pygame.draw.line(self.background, color, (0, y), (width, y))

    def _draw_color_wash(self, width: int, height: int) -> None:
        wash = pygame.Surface(self.size, pygame.SRCALPHA)
        bands = (
            (colors.SNAKE_GLOW, 7, pygame.Rect(0, int(height * 0.22), width, int(height * 0.28))),
            (colors.FOOD_GLOW, 6, pygame.Rect(0, int(height * 0.62), width, int(height * 0.20))),
            (colors.MAGENTA_ACCENT, 4, pygame.Rect(0, int(height * 0.06), width, int(height * 0.18))),
        )
        for color, alpha, rect in bands:
            pygame.draw.rect(wash, (*color, alpha), rect)
        self.background.blit(wash, (0, 0))

    def _draw_forest_floor_texture(self, width: int, height: int) -> None:
        texture = pygame.Surface(self.size, pygame.SRCALPHA)
        for index in range(42):
            x = (index * 149) % width
            y = height * 0.22 + ((index * 83) % int(height * 0.72))
            radius = 3 + (index % 4) * 2
            color = colors.BACKGROUND_GRID if index % 3 else colors.MOTE
            alpha = 9 if index % 3 else 6
            pygame.draw.circle(texture, (*color, alpha), (int(x), int(y)), radius)
        self.background.blit(texture, (0, 0))

    def _draw_grid(self, width: int, height: int) -> None:
        faint_line = (9, 31, 32)
        for y in range(0, height, CELL_SIZE):
            line_color = colors.BACKGROUND_GRID if y % (CELL_SIZE * 5) == 0 else faint_line
            pygame.draw.line(self.background, line_color, (0, y), (width, y), 1)

        for x in range(0, width, CELL_SIZE):
            line_color = colors.BACKGROUND_GRID if x % (CELL_SIZE * 5) == 0 else faint_line
            pygame.draw.line(self.background, line_color, (x, 0), (x, height), 1)

    def _build_vignette(self) -> None:
        width, height = self.size
        center = pygame.Vector2(width / 2, height / 2)
        max_distance = center.length()

        for y in range(0, height, 4):
            for x in range(0, width, 4):
                distance = pygame.Vector2(x - center.x, y - center.y).length()
                edge = max(0.0, distance / max_distance - 0.36)
                alpha = int(min(122, edge * 172))
                pygame.draw.rect(self.vignette, (*colors.VIGNETTE, alpha), (x, y, 4, 4))
