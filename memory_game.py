import os
import random
import select
import sys
import time

# Windows / macOS / Linux terminal input
if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty


ICONS = [
    "🍎", "🍌", "🍇", "🍉", "🍓", "🍒",
    "🍍", "🥝", "🍋", "🥥", "🥑", "🍆",
    "🥕", "🌽", "🍿", "🍩", "🍕", "🍔"
]

TURN_TIME = 30

PLAYERS = [
    {"name": "Player 1", "score": 0},
    {"name": "Player 2", "score": 0}
]


# ============================================================
# TERMINAL CONTROL
# ============================================================

def clear_screen():
    """Clear the terminal and move cursor to the top-left."""
    print("\033[2J\033[H", end="", flush=True)


def move_cursor_home():
    """Move cursor to the top-left without clearing."""
    print("\033[H", end="", flush=True)


def hide_cursor():
    print("\033[?25l", end="", flush=True)


def show_cursor():
    print("\033[?25h", end="", flush=True)


def clear_current_line():
    print("\033[2K", end="", flush=True)


# ============================================================
# INPUT HANDLING
# ============================================================

class TerminalInput:
    """
    Cross-platform single-key input.

    Windows:
        Uses msvcrt.

    macOS/Linux:
        Uses termios + select.
    """

    def __init__(self):
        self.old_settings = None

    def start(self):
        if os.name != "nt":
            fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)

    def stop(self):
        if os.name != "nt" and self.old_settings is not None:
            fd = sys.stdin.fileno()
            termios.tcsetattr(
                fd,
                termios.TCSADRAIN,
                self.old_settings
            )
            self.old_settings = None

    def key_available(self):
        if os.name == "nt":
            return msvcrt.kbhit()

        ready, _, _ = select.select(
            [sys.stdin],
            [],
            [],
            0
        )

        return bool(ready)

    def get_key(self):
        if os.name == "nt":

            if not msvcrt.kbhit():
                return None

            key = msvcrt.getwch()

            # Handle special Windows keys
            if key in ("\x00", "\xe0"):
                msvcrt.getwch()
                return None

            return key

        if not self.key_available():
            return None

        return sys.stdin.read(1)


terminal_input = TerminalInput()


# ============================================================
# EXIT CONFIRMATION
# ============================================================

def confirm_exit():
    """
    Ask for exit confirmation.

    Returns True if the user wants to exit.
    """

    terminal_input.stop()
    show_cursor()

    print()
    print("Are you sure you want to exit?")
    print("All current progress will be lost.")
    print()

    while True:

        choice = input("Exit? (y/n): ").strip().lower()

        if choice in ("y", "yes"):
            clear_screen()
            print("Goodbye.")
            return True

        if choice in ("n", "no"):
            hide_cursor()
            terminal_input.start()
            return False

        print("Please enter y or n.")


# ============================================================
# GAME SETUP
# ============================================================

def choose_mode():

    while True:

        clear_screen()
        show_cursor()

        print("=" * 50)
        print(f"{'MEMORY GAME':^50}")
        print("=" * 50)
        print()

        print("Select difficulty:")
        print()
        print("1. Easy  - 4 x 4")
        print("2. Hard  - 6 x 6")
        print("3. Exit")
        print()

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            return "easy"

        if choice == "2":
            return "hard"

        if choice == "3":
            clear_screen()
            print("Goodbye.")
            sys.exit()

        print()
        print("Invalid choice.")
        time.sleep(1)


def create_board(mode):

    if mode == "easy":
        number_of_pairs = 8
    else:
        number_of_pairs = 18

    selected_icons = ICONS[:number_of_pairs]

    cards = selected_icons + selected_icons.copy()

    random.shuffle(cards)

    return cards


def get_board_size(cards):

    if len(cards) == 16:
        return 4

    return 6


# ============================================================
# BOARD
# ============================================================

def format_card(value, revealed, matched):

    if matched:
        return "     "

    if revealed:
        return f" {value} "

    return "  ?  "


def display_board(cards, revealed, matched):

    size = get_board_size(cards)

    print()

    # Column numbers
    header = "       "

    for column in range(size):
        header += f"{column + 1:^8}"

    print("\033[2K" + header)

    separator = "      " + "-" * (size * 8)

    print("\033[2K" + separator)

    for row in range(size):

        row_text = f"  {chr(65 + row)}   "

        for column in range(size):

            index = row * size + column

            if matched[index]:
                card = "       "

            elif revealed[index]:
                card = f" {cards[index]} "

            else:
                card = "   ?   "

            row_text += f"|{card:^7}"

        row_text += "|"

        # Clear the entire terminal line before drawing it.
        print("\033[2K" + row_text)

        print("\033[2K" + separator)

    print()

# ============================================================
# COORDINATE HANDLING
# ============================================================

def coordinate_to_index(coordinate, size):

    coordinate = coordinate.strip().upper()

    if len(coordinate) < 2:
        return None

    row_char = coordinate[0]
    column_text = coordinate[1:]

    if not row_char.isalpha():
        return None

    if not column_text.isdigit():
        return None

    row = ord(row_char) - ord("A")

    column = int(column_text) - 1

    if row < 0 or row >= size:
        return None

    if column < 0 or column >= size:
        return None

    return row * size + column


# ============================================================
# RENDERING
# ============================================================

def render_game(
    cards,
    revealed,
    matched,
    current_player,
    mode,
    remaining,
    message="",
    input_buffer="",
    prompt=""
):

    move_cursor_home()

    # Header
    print("=" * 50)

    size = get_board_size(cards)

    print(
        f"{f'MEMORY GAME - {mode.upper()} {size} x {size}':^50}"
    )

    print("=" * 50)

    # Score
    print(
        f"Player 1: {PLAYERS[0]['score']}    "
        f"Player 2: {PLAYERS[1]['score']}"
    )

    print(
        f"Turn: {PLAYERS[current_player]['name']}"
    )

    print(
        f"Time remaining: {remaining:02d} seconds"
    )

    print("=" * 50)

    # Board
    display_board(
        cards,
        revealed,
        matched
    )

    # Always print a fixed-width message line.
    # This prevents old messages from remaining.
    message_line = message[:48]

    print(f"{message_line:<48}")

    # Input line
    input_line = prompt + input_buffer

    print(f"{input_line:<48}", end="", flush=True)

    # Clear everything below the current screen.
    print("\033[J", end="", flush=True)


# ============================================================
# INPUT BUFFER
# ============================================================

def get_coordinate_input(
    cards,
    revealed,
    matched,
    current_player,
    mode,
    deadline,
    prompt
):

    size = get_board_size(cards)

    input_buffer = ""

    message = ""

    while True:

        remaining = max(
            0,
            int(deadline - time.time())
        )

        if remaining <= 0:
            return None

        render_game(
            cards,
            revealed,
            matched,
            current_player,
            mode,
            remaining,
            message,
            input_buffer,
            prompt
        )

        message = ""

        key = terminal_input.get_key()

        if key is None:

            # Small delay prevents excessive CPU usage
            time.sleep(0.03)

            continue

        # Enter
        if key in ("\r", "\n"):

            choice = input_buffer.strip()

            if not choice:
                message = "Enter a card position."
                continue

            # Exit commands
            if choice.lower() in (
                "q",
                "quit",
                "exit"
            ):

                if confirm_exit():
                    sys.exit()

                input_buffer = ""
                continue

            index = coordinate_to_index(
                choice,
                size
            )

            if index is None:

                message = "Invalid position."

                input_buffer = ""

                continue

            if matched[index]:

                message = "That card has already been matched."

                input_buffer = ""

                continue

            if revealed[index]:

                message = "That card is already selected."

                input_buffer = ""

                continue

            return index

        # Backspace
        elif key in ("\x08", "\x7f"):

            input_buffer = input_buffer[:-1]

        # Ctrl+C
        elif key == "\x03":

            if confirm_exit():
                sys.exit()

            input_buffer = ""

        # Normal character
        elif key.isprintable():

            input_buffer += key


# ============================================================
# SHOW TEMPORARY MESSAGE
# ============================================================

def show_message(
    cards,
    revealed,
    matched,
    current_player,
    mode,
    message,
    seconds=2
):

    end_time = time.time() + seconds

    while time.time() < end_time:

        render_game(
            cards,
            revealed,
            matched,
            current_player,
            mode,
            max(
                0,
                int(end_time - time.time())
            ),
            message
        )

        time.sleep(0.05)


# ============================================================
# PLAY GAME
# ============================================================

def play_game(mode):

    # Reset scores
    for player in PLAYERS:
        player["score"] = 0

    cards = create_board(mode)

    revealed = [False] * len(cards)

    matched = [False] * len(cards)

    current_player = 0

    matched_pairs = 0

    total_pairs = len(cards) // 2

    clear_screen()
    hide_cursor()

    terminal_input.start()

    try:

        while matched_pairs < total_pairs:

            # ------------------------------------------------
            # START TURN
            # ------------------------------------------------

            turn_deadline = time.time() + TURN_TIME

            # ------------------------------------------------
            # FIRST CARD
            # ------------------------------------------------

            first_index = get_coordinate_input(
                cards,
                revealed,
                matched,
                current_player,
                mode,
                turn_deadline,
                "\nChoose first card: "
            )

            if first_index is None:

                show_message(
                    cards,
                    revealed,
                    matched,
                    current_player,
                    mode,
                    "Time is up."
                )

                current_player = 1 - current_player

                continue

            revealed[first_index] = True

            # ------------------------------------------------
            # CHECK TIME
            # ------------------------------------------------

            if time.time() >= turn_deadline:

                revealed[first_index] = False

                show_message(
                    cards,
                    revealed,
                    matched,
                    current_player,
                    mode,
                    "Time is up."
                )

                current_player = 1 - current_player

                continue

            # ------------------------------------------------
            # SECOND CARD
            # ------------------------------------------------

            second_index = get_coordinate_input(
                cards,
                revealed,
                matched,
                current_player,
                mode,
                turn_deadline,
                "\nChoose second card: "
            )

            if second_index is None:

                revealed[first_index] = False

                show_message(
                    cards,
                    revealed,
                    matched,
                    current_player,
                    mode,
                    "Time is up."
                )

                current_player = 1 - current_player

                continue

            revealed[second_index] = True

            # ------------------------------------------------
            # SHOW BOTH CARDS
            # ------------------------------------------------

            render_game(
                cards,
                revealed,
                matched,
                current_player,
                mode,
                max(
                    0,
                    int(turn_deadline - time.time())
                ),
                f"\nSelected: {cards[first_index]} "
                f"and {cards[second_index]}"
            )

            time.sleep(1)

            # ------------------------------------------------
            # MATCH
            # ------------------------------------------------

            if cards[first_index] == cards[second_index]:

                matched[first_index] = True

                matched[second_index] = True

                revealed[first_index] = False

                revealed[second_index] = False

                PLAYERS[current_player]["score"] += 1

                matched_pairs += 1

                if matched_pairs == total_pairs:
                    break

                show_message(
                    cards,
                    revealed,
                    matched,
                    current_player,
                    mode,
                    "Match. You get 1 point. Same player continues."
                )

            # ------------------------------------------------
            # NO MATCH
            # ------------------------------------------------

            else:

                revealed[first_index] = False

                revealed[second_index] = False

                next_player = 1 - current_player

                show_message(
                    cards,
                    revealed,
                    matched,
                    current_player,
                    mode,
                    "No match. Turn changes."
                )

                current_player = next_player

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        show_cursor()

        clear_screen()

        print("=" * 50)
        print(f"{'GAME OVER':^50}")
        print("=" * 50)

        print()

        print(
            f"Player 1: {PLAYERS[0]['score']}"
        )

        print(
            f"Player 2: {PLAYERS[1]['score']}"
        )

        print()

        if PLAYERS[0]["score"] > PLAYERS[1]["score"]:

            print("Player 1 wins.")

        elif PLAYERS[1]["score"] > PLAYERS[0]["score"]:

            print("Player 2 wins.")

        else:

            print("The game is a tie.")

        print()

        terminal_input.stop()

        while True:

            choice = input(
                "Play again? (y/n): "
            ).strip().lower()

            if choice in ("y", "yes"):

                hide_cursor()

                terminal_input.start()

                return True

            if choice in ("n", "no"):

                return False

            print("Please enter y or n.")

    finally:

        terminal_input.stop()
        show_cursor()


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        while True:

            mode = choose_mode()

            play_again = play_game(mode)

            if not play_again:
                break

    except KeyboardInterrupt:

        terminal_input.stop()
        show_cursor()
        clear_screen()

        print("Game exited.")

    finally:

        terminal_input.stop()
        show_cursor()


if __name__ == "__main__":
    main()