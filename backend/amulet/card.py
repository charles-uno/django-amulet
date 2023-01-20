"""
A single card is stored as a string. We use a class for a collection of cards.
"""


from typing import NamedTuple, Set, Tuple
import yaml

from .mana import Mana, mana
from .note import Note, NoteType
from . import helpers


with open("assets/card-data.yaml") as handle:
    CARD_DATA = yaml.safe_load(handle)


class Card(NamedTuple):
    name: str
    n_counters: int = 0

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    @property
    def slug(self) -> str:
        return helpers.slugify(self.name)

    @property
    def notes(self) -> Tuple[Note, ...]:
        ret = (Note(text=self.name, type=NoteType.CARD),)
        if self.n_counters:
            ret += (Note(text="*" * self.n_counters),)
        return ret

    @property
    def types(self) -> Set[str]:
        return set(CARD_DATA[self.name].get("type", "").split(","))

    @property
    def is_land(self) -> bool:
        return "land" in self.types

    @property
    def is_spell(self) -> bool:
        return not self.is_land

    @property
    def is_green_creature(self):
        return "creature" in self.types and self.mana_cost >= mana("G")

    @property
    def mana_cost(self) -> Mana:
        m = CARD_DATA[self.name].get("mana_cost")
        assert m is not None
        return mana(m)

    @property
    def enters_tapped(self) -> bool:
        return CARD_DATA[self.name].get("enters_tapped", False)

    @property
    def taps_for(self) -> Mana:
        return mana(CARD_DATA[self.name].get("taps_for", ""))

    @property
    def never_defer(self) -> bool:
        return CARD_DATA[self.name].get("never_defer", False)

    @property
    def is_saga(self) -> bool:
        return "saga" in self.types

    def plus_counter(self) -> "Card":
        return Card(name=self.name, n_counters=self.n_counters + 1)

    def without_counters(self) -> "Card":
        if self.n_counters == 0:
            return self
        return Card(name=self.name)
