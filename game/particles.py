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
        return max(0, min(255, int(150 * life_ratio)))


class ParticleSystem:
    def __init__(self, bounds: tuple[int, int], ambient_count: int = 34) -> None:
        self.bounds = bounds
        self.particles: list[Particle] = []
        self.ambient_particles: list[Particle] = []
        self._sprite_cache: dict[tuple[tuple[int, int, int], int, int], pygame.Surface] = {}
        self._create_ambient_particles(ambient_count)

    def _create_ambient_particles(self, count: int) -> None:
        width, height = self.bounds
        for _ in range(count):
            self.ambient_particles.append(
                Particle(
                    position=pygame.Vector2(random.randrange(width), random.randrange(height)),
                    velocity=pygame.Vector2(random.uniform(-3, 4), random.uniform(-7, -1.5)),
                    color=random.choice((colors.MOTE, colors.FOOD_GLOW, colors.TEXT_MUTED)),
                    radius=random.uniform(1.1, 2.6),
                    lifetime=1.0,
                    max_lifetime=1.0,
                    drift=random.uniform(0, math.tau),
                )
            )

# Creates issue with snake sizing
    def emit_food_burst(self, center: tuple[int, int]) -> None:
        for index in range(18):
            angle = (math.tau / 18) * index + random.uniform(-0.18, 0.18)
            speed = random.uniform(34, 92)
            velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.38, 0.72)
            self.particles.append(
                Particle(
                    position=pygame.Vector2(center),
                    velocity=velocity,
                    color=random.choice((colors.FOOD_GLOW, colors.SNAKE_GLOW, colors.MAGENTA_ACCENT)),
                    radius=random.uniform(2.0, 4.0),
                    lifetime=lifetime,
                    max_lifetime=lifetime,
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
            alpha = 28 + int(42 * (math.sin(elapsed_seconds * 0.9 + particle.drift + index) + 1) / 2)
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
        alpha = max(0, min(255, alpha))
        rounded_radius = max(1, int(radius))
        alpha_bucket = (alpha // 8) * 8
        cache_key = (color, rounded_radius, alpha_bucket)
        particle_surface = self._sprite_cache.get(cache_key)
        if particle_surface is None:
            size = max(4, rounded_radius * 7)
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            center = (size, size)
            pygame.draw.circle(
                particle_surface,
                (*color, max(12, alpha_bucket // 3)),
                center,
                rounded_radius * 3,
            )
            pygame.draw.circle(particle_surface, (*color, alpha_bucket), center, rounded_radius)
            self._sprite_cache[cache_key] = particle_surface
        size = particle_surface.get_width() // 2
        surface.blit(particle_surface, (position.x - size, position.y - size))
