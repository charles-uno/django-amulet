from pathlib import Path
from typing import NamedTuple, Set
import yaml

from .mana import Mana


_CARD_DATA = None


def _get_card_data(card_name: str):
    global _CARD_DATA
    if _CARD_DATA is None:
        # Root of the backend app
        base_dir = Path(__file__).resolve().parent.parent
        with open(f"{base_dir}/static/card-data.yaml") as handle:
            _CARD_DATA = yaml.safe_load(handle)
    try:
        return _CARD_DATA[card_name]
    except KeyError:
        raise ValueError(f"unknown card name: {repr(card_name)}")


class Card(str):
    @property
    def slug(self) -> str:
        text = self.replace("'", "").lower()
        for c in "-,.":
            text = text.replace(c, "")
        return text.replace(" ", "_")

    @property
    def types(self) -> Set[str]:
        return set(_get_card_data(self).get("type", "").split(","))

    @property
    def is_land(self) -> bool:
        return "land" in self.types

    @property
    def is_spell(self) -> bool:
        return not self.is_land

    @property
    def is_green_creature(self):
        return "creature" in self.types and self.mana_cost >= Mana.from_string("G")

    @property
    def mana_cost(self) -> Mana:
        m = _get_card_data(self).get("mana_cost")
        assert m is not None
        return Mana.from_string(m)

    @property
    def enters_tapped(self) -> bool:
        return _get_card_data(self).get("enters_tapped", False)

    @property
    def taps_for(self) -> Mana:
        return Mana.from_string(_get_card_data(self).get("taps_for", ""))

    @property
    def never_defer(self) -> bool:
        return _get_card_data(self).get("never_defer", False)

    @property
    def is_saga(self) -> bool:
        return "saga" in self.types


class CardWithCounters(NamedTuple):
    card: Card
    n_counters: int = 0

    def plus_counter(self) -> "CardWithCounters":
        return CardWithCounters(card=self.card, n_counters=self.n_counters + 1)