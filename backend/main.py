#!/usr/bin/env python3

from amulet.game_state_manager import GameStateManager


def main():
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)

    gsm = GameStateManager(deck_list)


if __name__ == "__main__":
    main()
