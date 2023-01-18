#!/usr/bin/env python3

import random
import amulet


def main():
    print("hello")

    m = amulet.Mana("2GG")

    print(m)
    print(m - "3")

    c = amulet.Card("Amulet of Vigor")
    print(c)

    library = ["Forest"] * 40 + ["Primeval Titan"] * 20
    random.shuffle(library)
    game = amulet.GameState(library=library, on_the_play=True)

    print(game)


if __name__ == "__main__":
    main()
