import collections
from typing import Optional
import yaml

from .mana import Mana, maybe_mana
from . import helpers


with open("assets/card-data.yaml") as handle:
    CARD_DATA = yaml.safe_load(handle)


CardBase = collections.namedtuple("CardBase", "name counter")


class Card(CardBase):
    def __new__(cls, name: CardBase | str, counter: int = 0) -> CardBase:
        if isinstance(name, CardBase):
            return name
        return CardBase.__new__(cls, name, counter)

    def __repr__(self):
        return f"Card({repr(self.name)}, {repr(self.counter)})"

    def __str__(self):
        return helpers.highlight(helpers.compress(self.name), "green")

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.name
        else:
            return other.name == self.name

    @property
    def cost(self) -> Optional[Mana]:
        return maybe_mana(CARD_DATA[self.name].get("cost"))

    @property
    def enters_tapped(self) -> bool:
        return CARD_DATA[self.name].get("enters_tapped", False)

    @property
    def taps_for(self) -> Mana:
        return Mana(CARD_DATA[self.name].get("taps_for"))


class CardsNotOrdered(tuple):
    def __new__(self, names):
        cards = [Card(x) for x in names]
        return tuple.__new__(self, sorted(cards))

    def __str__(self):
        blurbs = []
        for card in sorted(set(self)):
            n = self.count(card)
            if n > 1:
                blurbs.append(f"{n}*{card}")
            else:
                blurbs.append(str(card))
        return " ".join(blurbs)

    def __add__(self, other):
        if isinstance(other, str):
            other = Card(other)
        if isinstance(other, Card):
            other = [other]
        return CardsNotOrdered(list(self) + list(other))

    def __contains__(self, card):
        return tuple.__contains__(self, Card(card))


class CardsOrdered(tuple):
    def __new__(self, names):
        cards = [Card(x) for x in names]
        return tuple.__new__(self, cards)

    def __contains__(self, card):
        return tuple.__contains__(self, Card(card))
