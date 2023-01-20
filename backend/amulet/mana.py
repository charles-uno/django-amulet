"""
For simplicity, track only green mana and total mana. That means there's no
ambiguity when we tap lands or pay costs.
"""

from typing import NamedTuple, Tuple
from .note import Note, NoteType

from . import helpers


class Mana(NamedTuple):
    green: int = 0
    total: int = 0

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    def __eq__(self, other: "Mana") -> bool:
        return self.total == other.total and self.green == other.green

    def __ge__(self, other: "Mana"):
        return self.total >= other.total and self.green >= other.green

    def __le__(self, other: "Mana"):
        return self.total <= other.total and self.green <= other.green

    def __gt__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def __bool__(self) -> bool:
        return self.total > 0

    @property
    def name(self) -> str:
        if self.green == 0 or self.total > self.green:
            ret = str(self.total - self.green)
        else:
            ret = ""
        return ret + "G" * self.green

    def __add__(self, other: "Mana") -> "Mana":
        green = self.green + other.green
        total = self.total + other.total
        return Mana(green, total)

    def __sub__(self, other: "Mana") -> "Mana":
        # Sometimes we might have to pay a generic cost with green
        new_total = self.total - other.total
        new_green = min(self.green - other.green, new_total)
        return Mana(new_green, new_total)

    def __mul__(self, n: int) -> "Mana":
        return Mana(self.green * n, self.total * n)

    def __str__(self):
        return helpers.highlight(self.name, "magenta")

    @property
    def notes(self) -> Tuple[Note]:
        return (Note(self.name, NoteType.MANA),)


def mana(expr: str) -> Mana:
    n_green = expr.upper().count("G")
    digits_value = sum([int(x) for x in expr if x.isdigit()])
    symbols_value = len([x for x in expr if not x.isdigit()])
    return Mana(green=n_green, total=digits_value + symbols_value)
