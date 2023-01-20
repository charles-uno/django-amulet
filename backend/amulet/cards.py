from typing import Tuple
from .card import Card


class Cards(Tuple[Card, ...]):
    def __add__(self, c: Card) -> "Cards":
        return Cards(list(self) + [c])

    def __sub__(self, c: Card) -> "Cards":
        i = self.index(c)
        return Cards(self[:i] + self[i + 1 :])

    def __str__(self) -> str:
        return " ".join(str(c) for c in self)
