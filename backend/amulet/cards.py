from typing import List, Tuple

from .note import Note
from .card import Card


class Cards(Tuple[Card, ...]):
    def __add__(self, c: Card) -> "Cards":
        return Cards(list(self) + [c])

    def __sub__(self, c: Card) -> "Cards":
        i = self.index(c)
        return Cards(self[:i] + self[i + 1 :])

    def __str__(self) -> str:
        return " ".join(str(c) for c in self)

    @property
    def notes(self) -> Tuple[Note, ...]:
        ret = []
        for c in self:
            ret.append(Note(" "))
            ret.extend(c.notes)
        return tuple(ret[:-1])
