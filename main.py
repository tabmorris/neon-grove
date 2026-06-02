import pygame

from game.game_state import GameState
from game.input_handler import InputHandler
from game.renderer import Renderer
from settings import FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH


def main() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    game_state = GameState()
    input_handler = InputHandler()
    renderer = Renderer(screen)

    running = True
    while running:
        delta_seconds = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                input_handler.handle_event(event, game_state)

        game_state.update(delta_seconds)
        renderer.draw(game_state)

    pygame.quit()


if __name__ == "__main__":
    main()
