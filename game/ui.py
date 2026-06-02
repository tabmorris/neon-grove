from __future__ import annotations

import pygame

from utils import colors


class UI:
    def __init__(self) -> None:
        self.font_large = pygame.font.SysFont("arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("arial", 20)

    def draw_score(self, surface: pygame.Surface, score: int) -> None:
        text = self.font_medium.render(f"Score {score}", True, colors.TEXT)
        surface.blit(text, (28, 22))

    def draw_center_message(
        self,
        surface: pygame.Surface,
        title: str,
        subtitle: str,
        title_color: tuple[int, int, int] = colors.TEXT,
    ) -> None:
        width, height = surface.get_size()
        title_surface = self.font_large.render(title, True, title_color)
        subtitle_surface = self.font_small.render(subtitle, True, colors.TEXT_MUTED)

        title_rect = title_surface.get_rect(center=(width // 2, height // 2 - 28))
        subtitle_rect = subtitle_surface.get_rect(center=(width // 2, height // 2 + 26))

        panel_rect = pygame.Rect(0, 0, max(title_rect.width, subtitle_rect.width) + 96, 148)
        panel_rect.center = (width // 2, height // 2)

        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (*colors.PANEL, 218), panel.get_rect(), border_radius=8)
        pygame.draw.rect(panel, (*colors.SNAKE_GLOW, 70), panel.get_rect(), 1, border_radius=8)

        surface.blit(panel, panel_rect)
        surface.blit(title_surface, title_rect)
        surface.blit(subtitle_surface, subtitle_rect)
