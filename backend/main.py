#!/usr/bin/env python3

import amulet


def main():
    print("hello")

    m = amulet.Mana("2GG")

    print(m)

    print(m - "3")


if __name__ == "__main__":
    main()
