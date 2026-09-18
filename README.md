# Memory Game

A simple two-player memory game that runs directly in the terminal.

The goal is to find matching pairs of cards and score more points than the other player.

## How to Play

There are two players.

On each turn, select two cards using their position on the board.

For example:

A1  
B3

If the cards match:

- The player gets 1 point.
- The same player gets another turn.

If the cards do not match:

- The cards are hidden again.
- The turn moves to the other player.

Each player has 30 seconds to complete their turn.

The game ends when all pairs have been matched.

## Game Modes

### Easy

- 4 x 4 board
- 8 pairs
- 16 cards

### Hard

- 6 x 6 board
- 18 pairs
- 36 cards

The cards are randomly shuffled every time a new game starts.

## Controls

Card positions are not case-sensitive.

Both of these work:

```text
A1
a1

To exit during the game, enter:
q
You can also use:
quit
exit
The game asks for confirmation before exiting.

Run the Game
Requirements
Python 3 is required to run the source code directly.
Clone the repository:
git clone https://github.com/n33r0j/memory-game.git
cd memory-game
Run the game:
python3 memory_game.py

Download
Pre-built versions for Windows, macOS, and Linux will be available in the Releases section.
Download the version for your operating system and run the game from your terminal.
Project Structure
memory-game/
├── memory_game.py
├── README.md
└── .github/
    └── workflows/
        └── build.yml

License
This project is open source and available for learning and personal use.

