import unittest

import pygame

from game.particles import ParticleSystem


class ParticleSystemTest(unittest.TestCase):
    def test_food_burst_particles_have_valid_alpha(self) -> None:
        particle_system = ParticleSystem((1280, 720), ambient_count=0)

        particle_system.emit_food_burst((120, 120))

        self.assertTrue(particle_system.particles)
        for particle in particle_system.particles:
            self.assertGreaterEqual(particle.alpha, 0)
            self.assertLessEqual(particle.alpha, 255)

    def test_food_burst_draws_without_invalid_color(self) -> None:
        surface = pygame.Surface((240, 180), pygame.SRCALPHA)
        particle_system = ParticleSystem((240, 180), ambient_count=0)
        particle_system.emit_food_burst((120, 90))

        particle_system.draw_feedback(surface)


if __name__ == "__main__":
    unittest.main()
