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

    hand, library = library[:7], library[7:]

    state = amulet.GameState(library=library, hand=hand, on_the_play=True)
    states = state.next_states()

    print(states.pop().get_notes())


if __name__ == "__main__":
    main()
