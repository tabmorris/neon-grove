from __future__ import annotations

from typing import Iterable

import pygame


def grid_to_pixel(cell: tuple[int, int], cell_size: int) -> tuple[int, int]:
    return cell[0] * cell_size, cell[1] * cell_size


def draw_glow_circle(
    surface: pygame.Surface,
    center: tuple[int, int],
    color: tuple[int, int, int],
    radius: int,
    layers: int = 4,
) -> None:
    for index in range(layers, 0, -1):
        alpha = max(12, 52 - index * 8)
        glow_radius = radius + index * 7
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*color, alpha),
            (glow_radius, glow_radius),
            glow_radius,
        )
        surface.blit(glow_surface, (center[0] - glow_radius, center[1] - glow_radius))


def clamp_cells(cells: Iterable[tuple[int, int]]) -> set[tuple[int, int]]:
    return set(cells)
