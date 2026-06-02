from __future__ import annotations

from dataclasses import dataclass
import math
import random

import pygame

from utils import colors


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    radius: float
    lifetime: float
    max_lifetime: float
    drift: float = 0.0

    @property
    def alpha(self) -> int:
        life_ratio = max(0.0, self.lifetime / self.max_lifetime)
        return int(150 * life_ratio)


class ParticleSystem:
    def __init__(self, bounds: tuple[int, int], ambient_count: int = 34) -> None:
        self.bounds = bounds
        self.particles: list[Particle] = []
        self.ambient_particles: list[Particle] = []
        self._create_ambient_particles(ambient_count)

    def _create_ambient_particles(self, count: int) -> None:
        width, height = self.bounds
        for _ in range(count):
            self.ambient_particles.append(
                Particle(
                    position=pygame.Vector2(random.randrange(width), random.randrange(height)),
                    velocity=pygame.Vector2(random.uniform(-4, 5), random.uniform(-9, -2)),
                    color=random.choice((colors.MOTE, colors.FOOD_GLOW, colors.TEXT_MUTED)),
                    radius=random.uniform(1.2, 2.8),
                    lifetime=1.0,
                    max_lifetime=1.0,
                    drift=random.uniform(0, math.tau),
                )
            )

    def emit_food_burst(self, center: tuple[int, int]) -> None:
        for index in range(18):
            angle = (math.tau / 18) * index + random.uniform(-0.18, 0.18)
            speed = random.uniform(34, 92)
            velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(
                Particle(
                    position=pygame.Vector2(center),
                    velocity=velocity,
                    color=random.choice((colors.FOOD_GLOW, colors.SNAKE_GLOW, colors.MAGENTA_ACCENT)),
                    radius=random.uniform(2.0, 4.0),
                    lifetime=random.uniform(0.38, 0.72),
                    max_lifetime=random.uniform(0.38, 0.72),
                )
            )

    def update(self, delta_seconds: float) -> None:
        width, height = self.bounds

        for particle in self.ambient_particles:
            particle.drift += delta_seconds * 0.9
            particle.position += particle.velocity * delta_seconds
            particle.position.x += math.sin(particle.drift) * 5 * delta_seconds
            if particle.position.y < -12:
                particle.position.y = height + 12
                particle.position.x = random.randrange(width)
            if particle.position.x < -12:
                particle.position.x = width + 12
            elif particle.position.x > width + 12:
                particle.position.x = -12

        live_particles: list[Particle] = []
        for particle in self.particles:
            particle.lifetime -= delta_seconds
            if particle.lifetime <= 0:
                continue
            particle.velocity *= 0.96
            particle.position += particle.velocity * delta_seconds
            live_particles.append(particle)
        self.particles = live_particles

    def draw_ambient(self, surface: pygame.Surface, elapsed_seconds: float) -> None:
        for index, particle in enumerate(self.ambient_particles):
            alpha = 38 + int(34 * (math.sin(elapsed_seconds * 1.2 + index) + 1) / 2)
            self._draw_particle(surface, particle.position, particle.color, particle.radius, alpha)

    def draw_feedback(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            self._draw_particle(surface, particle.position, particle.color, particle.radius, particle.alpha)

    def _draw_particle(
        self,
        surface: pygame.Surface,
        position: pygame.Vector2,
        color: tuple[int, int, int],
        radius: float,
        alpha: int,
    ) -> None:
        size = max(4, int(radius * 7))
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        center = (size, size)
        pygame.draw.circle(particle_surface, (*color, max(16, alpha // 3)), center, int(radius * 3))
        pygame.draw.circle(particle_surface, (*color, alpha), center, max(1, int(radius)))
        surface.blit(particle_surface, (position.x - size, position.y - size))
