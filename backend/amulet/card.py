"""
A single card is stored as a string. We use a class for a collection of cards.
"""


from typing import NamedTuple, Optional
import yaml

from .mana import Mana, maybe_mana
from . import helpers


with open("assets/card-data.yaml") as handle:
    CARD_DATA = yaml.safe_load(handle)


class CardBase(NamedTuple):
    name: str

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    def __eq__(self, other: Card) -> bool:
        return other.name == self.name


class Card(CardBase):
    @property
    def slug(self) -> str:
        return helpers.slugify(self.name)

    def __repr__(self):
        return f"Card({repr(self.name)})"

    def __str__(self):
        return helpers.highlight(helpers.squish(self.name), "green")

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
