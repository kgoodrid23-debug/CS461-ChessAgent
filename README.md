# CS461 Chess Agent

CS 461 Final Project: Python chess agent that using minimax with alpha-beta pruning

## Current Features

- Lets you play a command-line chess game against the AI
- Uses minimax with alpha-beta pruning to choose moves
- Uses a piece-square-table evaluation function
- Includes basic move ordering to help the search run better
- Can create a Jupyter notebook board visualization in chessVisual.ipynb

## Setup / Requirements

This Project uses Python 3.10+ and packages are listed in requirements.txt

To install everything you need, run:

python -m pip install -r requirements.txt

## Run the Program

From the project folder:

python chessAgent.py

When the game stats, it will ask:

- Your color (w or b)
- Difficulty (1, 2, or 3)
- Enter moves in UCI (e2e4) or SAN (Nf3) format

Useful commands while playing:

- type 'quit' to exit
- type 'undo' to take back the last two moves

## Notes

- The CLI version only needs python-chess installed to workl
- If the Jupyter packages are missing, the game will show a notice and continue as normal
