from __future__ import annotations

import pygame

from utils import colors


class UI:
    def __init__(self) -> None:
        self.font_title = pygame.font.SysFont("arial", 72, bold=True)
        self.font_large = pygame.font.SysFont("arial", 46, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("arial", 20)

    def draw_score(self, surface: pygame.Surface, score: int) -> None:
        glow = self.font_medium.render(f"Score {score}", True, colors.TEXT_GLOW)
        text = self.font_medium.render(f"Score {score}", True, colors.TEXT)
        surface.blit(glow, (30, 24))
        surface.blit(text, (28, 22))

    def draw_title(self, surface: pygame.Surface) -> None:
        self.draw_center_message(
            surface,
            "Neon Grove",
            "Press Enter, Space, or move to begin",
            title_color=colors.SNAKE_HEAD,
            title_font=self.font_title,
            footer="WASD / Arrows to move   |   P or Esc to pause",
        )

    def draw_pause(self, surface: pygame.Surface) -> None:
        self.draw_center_message(
            surface,
            "Paused",
            "Press Enter, Space, P, or Esc to continue",
            title_color=colors.TEXT,
        )

    def draw_game_over(self, surface: pygame.Surface, score: int) -> None:
        self.draw_center_message(
            surface,
            "Game Over",
            f"Final score {score}   |   Press Enter or Space to restart",
            title_color=colors.WARNING,
        )

    def draw_center_message(
        self,
        surface: pygame.Surface,
        title: str,
        subtitle: str,
        title_color: tuple[int, int, int] = colors.TEXT,
        title_font: pygame.font.Font | None = None,
        footer: str | None = None,
    ) -> None:
        width, height = surface.get_size()
        title_font = title_font or self.font_large
        glow_surface = title_font.render(title, True, colors.TEXT_GLOW)
        title_surface = title_font.render(title, True, title_color)
        subtitle_surface = self.font_small.render(subtitle, True, colors.TEXT_MUTED)
        footer_surface = self.font_small.render(footer, True, colors.TEXT_MUTED) if footer else None

        title_rect = title_surface.get_rect(center=(width // 2, height // 2 - 34))
        glow_rect = glow_surface.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))
        subtitle_rect = subtitle_surface.get_rect(center=(width // 2, height // 2 + 24))
        footer_rect = footer_surface.get_rect(center=(width // 2, height // 2 + 62)) if footer_surface else None

        content_width = max(title_rect.width, subtitle_rect.width, footer_rect.width if footer_rect else 0)
        panel_height = 192 if footer_surface else 152
        panel_rect = pygame.Rect(0, 0, content_width + 112, panel_height)
        panel_rect.center = (width // 2, height // 2)

        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (*colors.PANEL, 205), panel.get_rect(), border_radius=8)
        pygame.draw.rect(panel, (*colors.SNAKE_GLOW, 86), panel.get_rect(), 1, border_radius=8)

        surface.blit(panel, panel_rect)
        surface.blit(glow_surface, glow_rect)
        surface.blit(title_surface, title_rect)
        surface.blit(subtitle_surface, subtitle_rect)
        if footer_surface and footer_rect:
            surface.blit(footer_surface, footer_rect)
