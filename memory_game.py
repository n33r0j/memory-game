import random
import time
import os
import sys
import select


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


def clear_screen():
    os.system("clear")


def print_header(title):
    print("\n" + "=" * 50)
    print(f"{title:^50}")
    print("=" * 50)


def choose_mode():

    while True:

        clear_screen()

        print_header("MEMORY GAME")

        print("\nSelect difficulty:\n")
        print("1. Easy  - 4 x 4")
        print("2. Hard  - 6 x 6")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            return "easy"

        if choice == "2":
            return "hard"

        if choice == "3":
            print("\nGoodbye.")
            sys.exit()

        print("\nInvalid choice.")
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


def format_card(value, revealed, matched):

    if matched:
        return "[   ]"

    if revealed:
        return f"[ {value} ]"

    return "[ ? ]"


def display_board(cards, revealed, matched):

    size = get_board_size(cards)

    print()

    print("       ", end="")

    for column in range(size):
        print(f"{column + 1:^7}", end="")

    print()

    print("      " + "-" * (size * 7))

    for row in range(size):

        print(f"  {chr(65 + row)}   ", end="")

        for column in range(size):

            index = row * size + column

            card = format_card(
                cards[index],
                revealed[index],
                matched[index]
            )

            print(f"{card:^7}", end="")

        print()

        print("      " + "-" * (size * 7))

    print()


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


def confirm_exit():

    print("\nAre you sure you want to exit?")
    print("All current progress will be lost.")

    while True:

        confirmation = input(
            "Exit? (y/n): "
        ).strip().lower()

        if confirmation in ("y", "yes"):
            print("\nExiting game.")
            time.sleep(1)
            sys.exit()

        if confirmation in ("n", "no"):
            print("\nContinuing game.")
            time.sleep(1)
            return

        print("Please enter y or n.")


def get_input_with_timer(prompt, timeout):

    print(prompt, end="", flush=True)

    ready, _, _ = select.select(
        [sys.stdin],
        [],
        [],
        timeout
    )

    if ready:
        return sys.stdin.readline().strip()

    return None


def display_scoreboard(current_player, timer=None):

    print("=" * 50)

    print(
        f"Player 1: {PLAYERS[0]['score']}    "
        f"Player 2: {PLAYERS[1]['score']}"
    )

    print(
        f"Turn: {PLAYERS[current_player]['name']}"
    )

    if timer is not None:
        print(f"Time remaining: {timer} seconds")

    print("=" * 50)


def timed_card_selection(
    cards,
    revealed,
    matched,
    current_player,
    timeout,
    message
):

    size = get_board_size(cards)

    start_time = time.time()

    while True:

        elapsed = time.time() - start_time
        remaining = max(0, int(timeout - elapsed))

        if remaining <= 0:
            return None

        clear_screen()

        display_scoreboard(
            current_player,
            remaining
        )

        display_board(
            cards,
            revealed,
            matched
        )

        choice = get_input_with_timer(
            message,
            remaining
        )

        if choice is None:
            return None

        choice = choice.strip()

        if choice.lower() in ("q", "quit", "exit"):

            confirm_exit()

            continue

        index = coordinate_to_index(
            choice,
            size
        )

        if index is None:

            print("\nInvalid position.")
            time.sleep(1)

            continue

        if matched[index]:

            print("\nThat card has already been matched.")
            time.sleep(1)

            continue

        if revealed[index]:

            print("\nThat card is already selected.")
            time.sleep(1)

            continue

        return index


def hard_mode_first_card_warning():

    print("\nRemember this card.")
    time.sleep(1)


def end_game():

    clear_screen()

    print_header("GAME OVER")

    player1_score = PLAYERS[0]["score"]
    player2_score = PLAYERS[1]["score"]

    print()
    print(f"Player 1: {player1_score}")
    print(f"Player 2: {player2_score}")
    print()

    if player1_score > player2_score:

        print("Player 1 wins.")

    elif player2_score > player1_score:

        print("Player 2 wins.")

    else:

        print("The game is a tie.")

    print()


def play_game(mode):

    for player in PLAYERS:
        player["score"] = 0

    cards = create_board(mode)

    size = get_board_size(cards)

    revealed = [False] * len(cards)
    matched = [False] * len(cards)

    current_player = 0

    matched_pairs = 0
    total_pairs = len(cards) // 2

    while matched_pairs < total_pairs:

        clear_screen()

        print_header(
            f"MEMORY GAME - {mode.upper()} {size} x {size}"
        )

        print(
            f"\nPlayer 1: {PLAYERS[0]['score']}    "
            f"Player 2: {PLAYERS[1]['score']}"
        )

        print(
            f"Turn: {PLAYERS[current_player]['name']}"
        )

        turn_start = time.time()

        remaining_time = TURN_TIME - (
            time.time() - turn_start
        )

        first_index = timed_card_selection(
            cards,
            revealed,
            matched,
            current_player,
            remaining_time,
            "\nChoose first card: "
        )

        if first_index is None:

            clear_screen()

            print_header("TIME UP")

            print(
                f"\n{PLAYERS[current_player]['name']} "
                "ran out of time."
            )

            current_player = 1 - current_player

            time.sleep(1.5)

            continue

        revealed[first_index] = True

        clear_screen()

        print_header(
            f"MEMORY GAME - {mode.upper()} {size} x {size}"
        )

        print(
            f"\nPlayer 1: {PLAYERS[0]['score']}    "
            f"Player 2: {PLAYERS[1]['score']}"
        )

        print(
            f"Turn: {PLAYERS[current_player]['name']}"
        )

        display_board(
            cards,
            revealed,
            matched
        )

        print(
            f"\nFirst card: {cards[first_index]}"
        )

        if mode == "hard":

            hard_mode_first_card_warning()

        elapsed = time.time() - turn_start

        remaining_time = TURN_TIME - elapsed

        if remaining_time <= 0:

            revealed[first_index] = False

            print("\nTime up.")

            current_player = 1 - current_player

            time.sleep(1.5)

            continue

        second_index = timed_card_selection(
            cards,
            revealed,
            matched,
            current_player,
            remaining_time,
            "\nChoose second card: "
        )

        if second_index is None:

            revealed[first_index] = False

            clear_screen()

            print_header("TIME UP")

            print(
                f"\n{PLAYERS[current_player]['name']} "
                "ran out of time."
            )

            current_player = 1 - current_player

            time.sleep(1.5)

            continue

        revealed[second_index] = True

        clear_screen()

        print_header(
            f"MEMORY GAME - {mode.upper()} {size} x {size}"
        )

        display_scoreboard(current_player)

        display_board(
            cards,
            revealed,
            matched
        )

        first_card = cards[first_index]
        second_card = cards[second_index]

        print(
            f"\nSelected: {first_card} and {second_card}"
        )

        if first_card == second_card:

            print("\nMatch.")

            matched[first_index] = True
            matched[second_index] = True

            revealed[first_index] = False
            revealed[second_index] = False

            PLAYERS[current_player]["score"] += 1

            matched_pairs += 1

            print(
                f"{PLAYERS[current_player]['name']} "
                "gets 1 point."
            )

            print("Same player continues.")

            time.sleep(1.5)

        else:

            print("\nNo match.")

            time.sleep(1.5)

            revealed[first_index] = False
            revealed[second_index] = False

            current_player = 1 - current_player

            print(
                f"\nTurn changes to "
                f"{PLAYERS[current_player]['name']}."
            )

            time.sleep(1.5)

    end_game()

    while True:

        choice = input(
            "Play again? (y/n): "
        ).strip().lower()

        if choice in ("y", "yes"):
            return True

        if choice in ("n", "no"):

            print("\nThanks for playing.")
            return False

        print("Please enter y or n.")


def main():

    while True:

        mode = choose_mode()

        play_again = play_game(mode)

        if not play_again:
            break


if __name__ == "__main__":
    main()