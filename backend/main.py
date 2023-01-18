#!/usr/bin/env python3

from amulet.game_state_manager import GameStateManager


def main():

    deck_list = ["Forest"] * 40 + ["Primeval Titan"] * 20
    gsm = GameStateManager(deck_list)


if __name__ == "__main__":
    main()
