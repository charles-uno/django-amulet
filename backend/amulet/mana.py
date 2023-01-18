"""
For simplicity, track only green mana and total mana. That means there's no
ambiguity when we tap lands or pay costs.
"""

import collections
from typing import Optional, Tuple

from . import helpers

ManaBase = collections.namedtuple("Mana", "green total")


class Mana(ManaBase):
    def __new__(cls, expr: str | Tuple[int, int]) -> ManaBase:
        if isinstance(expr, str):
            n_green = expr.upper().count("G")
            digits_value = sum([int(x) for x in expr if x.isdigit()])
            symbols_value = len([x for x in expr if not x.isdigit()])
            return super().__new__(cls, n_green, digits_value + symbols_value)
        elif isinstance(expr, tuple):
            assert len(expr) == 2
            green, total = expr
            assert total >= green
            assert total >= 0
            return super().__new__(cls, green, total)
        else:
            raise ValueError("unable to construct from " + repr(expr))

    def name(self) -> str:
        if self.green == 0 or self.total > self.green:
            ret = str(self.total - self.green)
        else:
            ret = ""
        return ret + "G" * self.green

    def __add__(self, other: ManaBase | str) -> ManaBase:
        other = Mana(other)
        green = self.green + other.green
        total = self.total + other.total
        return Mana((green, total))

    def __sub__(self, other: ManaBase | str) -> ManaBase:
        other = Mana(other)
        # Sometimes we might have to pay a generic cost with green
        new_total = self.total - other.total
        new_green = min(self.green - other.green, new_total)
        return Mana((new_green, new_total))

    def __str__(self):
        return helpers.highlight(self.name(), "magenta")

    def __repr__(self):
        return "Mana(" + repr(self.name()) + ")"

    def __bool__(self):
        return self.total > 0

    def __ge__(self, other):
        return self.total >= other.total and self.green >= other.green

    def __le__(self, other):
        return self.total <= other.total and self.green <= other.green


def maybe_mana(m: Optional[str]) -> Optional[Mana]:
    return None if m is None else Mana(m)
