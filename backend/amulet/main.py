from typing import Tuple, List, Set

from .game_manager import GameManager


def run_and_print_pretty(deck_list):
    opener = GameManager.get_opener_from_deck_list(deck_list)
    notes = GameManager.run_from_opener(opener)
    to_print = "".join(n.get_pretty() for n in notes)
    print(to_print)
