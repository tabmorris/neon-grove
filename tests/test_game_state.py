from collections import deque
import unittest

from game.game_state import GameState
from utils.constants import DIRECTION_LEFT, DIRECTION_RIGHT, PlayState


class GameStateTest(unittest.TestCase):
    def test_snake_cannot_immediately_reverse(self) -> None:
        state = GameState()

        state.snake.queue_direction(DIRECTION_LEFT)

        self.assertEqual(state.snake.pending_direction, DIRECTION_RIGHT)

    def test_eating_food_increases_score_and_growth(self) -> None:
        state = GameState()
        state.play_state = PlayState.PLAYING
        next_head = (state.snake.head[0] + 1, state.snake.head[1])
        state.food.position = next_head

        state._step()

        self.assertEqual(state.score, 1)
        self.assertEqual(state.snake.grow_pending, 1)
        self.assertEqual(state.consume_collection_cell(), next_head)

    def test_wall_collision_ends_game(self) -> None:
        state = GameState()
        state.play_state = PlayState.PLAYING
        state.snake.body = deque([(0, 0)])
        state.snake.direction = DIRECTION_LEFT
        state.snake.pending_direction = DIRECTION_LEFT

        state._step()

        self.assertEqual(state.play_state, PlayState.GAME_OVER)

    def test_pause_toggles_only_active_gameplay(self) -> None:
        state = GameState()

        state.toggle_pause()
        self.assertEqual(state.play_state, PlayState.TITLE)

        state.start()
        state.toggle_pause()
        self.assertEqual(state.play_state, PlayState.PAUSED)

        state.toggle_pause()
        self.assertEqual(state.play_state, PlayState.PLAYING)


if __name__ == "__main__":
    unittest.main()
