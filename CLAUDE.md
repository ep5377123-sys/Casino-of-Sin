# Casino of Sin

Multi-room text + GUI casino game. CSC 102 capstone project.
Player starts with debt and must gamble to repay it or face consequences.

## Run (text mode)
```bash
pip install -r requirements.txt
python casino_of_sin.py
```

## Run (GUI mode)
```bash
python gui_room_adventure.py
```

## Key Files
- casino_of_sin.py      — main game loop, room navigation
- casino_rooms.py       — Room class definition
- game.py               — core game logic
- death.py              — death/lose screen
- winner.py             — win screen
- gui_room_adventure.py — tkinter GUI version
- games/blackjack.py    — blackjack mini-game
- games/roulette.py     — roulette mini-game
- games/spin_wheel.py   — spin the wheel mini-game
- games/cock_fight.py   — cockfight mini-game

## Dependencies
- tkinter (built into Python)
- Pillow (for images in GUI mode) — install via requirements.txt
