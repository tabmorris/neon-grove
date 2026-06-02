# Neon Grove

Neon Grove is a cozy, bioluminescent reimagining of classic Snake built with Python and Pygame.

## Phase 1

This first pass focuses on a stable, playable foundation:

- grid-based snake movement
- WASD and arrow-key controls
- food spawning and growth
- score tracking
- collision and game-over states
- restart support
- lightweight neon forest rendering

## Run

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Controls

- Arrow keys or WASD: move
- Space or Enter: start / restart
- Escape: quit

## Architecture

- `main.py`: Pygame setup and the application loop.
- `game/game_state.py`: gameplay rules, timing, scoring, and state transitions.
- `game/snake.py`: snake body, movement, growth, and collision helpers.
- `game/food.py`: food placement that avoids the snake.
- `game/input_handler.py`: keyboard input mapped into gameplay actions.
- `game/renderer.py`: visual presentation and UI overlays.
- `utils/colors.py`: shared palette values.
