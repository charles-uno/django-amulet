from pathlib import Path
from typing import NamedTuple, Set
import yaml

from .mana import Mana, mana

# Root of the amulet_backend project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


with open(f"{BASE_DIR}/assets/card-data.yaml") as handle:
    CARD_DATA = yaml.safe_load(handle)


class Card(NamedTuple):
    name: str
    n_counters: int = 0

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    @property
    def slug(self) -> str:
        text = self.name.replace("'", "").lower()
        for c in "-,.":
            text = text.replace(c, "")
        return text.replace(" ", "_")

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


def card(card_name) -> Card:
    if card_name not in CARD_DATA:
        raise ValueError(f"unknown card: {repr(card_name)}")
    return Card(card_name)
