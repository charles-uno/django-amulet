#!/usr/bin/env python3

from typing import List
import amulet


def main():
    deck_list = load_deck_list()
    amulet.run_and_print_pretty(deck_list)


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list


if __name__ == "__main__":
    main()
