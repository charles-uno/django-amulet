"""
A single card is stored as a string. We use a class for a collection of cards.
"""


import collections
from typing import Optional
import yaml

from .mana import Mana, maybe_mana
from . import helpers


with open("assets/card-data.yaml") as handle:
    CARD_DATA = yaml.safe_load(handle)


CardBase = collections.namedtuple("CardBase", "name")


class Card(CardBase):
    def __new__(cls, name: CardBase | str) -> CardBase:
        if isinstance(name, CardBase):
            return name
        return CardBase.__new__(cls, name)

    @property
    def slug(self) -> str:
        return helpers.slugify(self.name)

    def __repr__(self):
        return f"Card({repr(self.name)})"

    def __str__(self):
        return helpers.highlight(helpers.squish(self.name), "green")

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.name
        else:
            return other.name == self.name

    @property
    def is_land(self) -> bool:
        return "land" in CARD_DATA[self.name].get("type", "")

    @property
    def is_spell(self) -> bool:
        return not self.is_land

    @property
    def cost(self) -> Optional[Mana]:
        return maybe_mana(CARD_DATA[self.name].get("cost"))

    @property
    def enters_tapped(self) -> bool:
        return CARD_DATA[self.name].get("enters_tapped", False)

    @property
    def taps_for(self) -> Mana:
        return Mana(CARD_DATA[self.name].get("taps_for"))


class Cards(tuple):
    def __new__(self, names):
        cards = [Card(x) for x in names]
        return tuple.__new__(self, cards)

    def __str__(self):
        blurbs = []
        for card in sorted(set(self)):
            n = self.count(card)
            if n > 1:
                blurbs.append(f"{n}*{card}")
            else:
                blurbs.append(str(card))
        return " ".join(blurbs)

    def __add__(self, c: str | Card) -> "Cards":
        return Cards(list(self) + [Card(c)])

    def __sub__(self, c: str | Card) -> "Cards":
        ret = list(self)
        ret.remove(Card(c))
        return Cards(ret)

    def __contains__(self, c: str | Card):
        return tuple.__contains__(self, Card(c))

    def count(self, c: str | Card) -> int:
        return self.count(Card(c))
