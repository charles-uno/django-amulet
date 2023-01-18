"""
For simplicity, track only green mana and total mana. That means there's no
ambiguity when we tap lands or pay costs.
"""

import collections
from typing import Optional, Tuple, NamedTuple

from . import helpers


class ManaBase(NamedTuple):
    green: int = 0
    total: int = 0

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    def __eq__(self, other: "ManaBase") -> bool:
        return self.total == other.total and self.green == other.green

    def __ge__(self, other: "ManaBase"):
        return self.total >= other.total and self.green >= other.green

    def __le__(self, other: "ManaBase"):
        return self.total <= other.total and self.green <= other.green


class Mana(ManaBase):
    def __new__(cls, expr: str = ""):
        n_green = expr.upper().count("G")
        digits_value = sum([int(x) for x in expr if x.isdigit()])
        symbols_value = len([x for x in expr if not x.isdigit()])
        return super().__new__(cls, n_green, digits_value + symbols_value)

    @property
    def name(self) -> str:
        if self.green == 0 or self.total > self.green:
            ret = str(self.total - self.green)
        else:
            ret = ""
        return ret + "G" * self.green

    def __add__(self, other: ManaBase) -> "Mana":
        green = self.green + other.green
        total = self.total + other.total
        return super().__new__(Mana, green, total)

    def __sub__(self, other: ManaBase) -> "Mana":
        # Sometimes we might have to pay a generic cost with green
        new_total = self.total - other.total
        new_green = min(self.green - other.green, new_total)
        return super().__new__(Mana, new_green, new_total)

    def __str__(self):
        return helpers.highlight(self.name, "magenta")

    def __repr__(self):
        return f"Mana(green={self.green}, total={self.total})"


def maybe_mana(m: Optional[str]) -> Optional[Mana]:
    return None if m is None else Mana(m)
