"""
To be run with pytest
"""

from ..game_state import GameState
from ..card import Card, CardWithCounters
from ..mana import Mana


def test_play_land():
    for card_name in ["Forest", "Bojuka Bog", "Radiant Fountain"]:
        c = Card(card_name)
        state = GameState(hand=(c,), battlefield=(), land_plays_remaining=1)
        next_state = state.maybe_play_land(c).pop()
        assert next_state.battlefield == (CardWithCounters(c, 0),)
        assert next_state.hand == ()


def test_cast_spell():
    for card_name in [
        "Dryad of the Ilysian Grove",
        "Amulet of Vigor",
        "Azusa, Lost but Seeking",
    ]:
        c = Card(card_name)
        state = GameState(
            hand=(c,),
            battlefield=(),
            mana_pool=c.mana_cost,
        )
        next_state = state.maybe_cast_spell(c).pop()
        assert next_state.hand == ()
        assert next_state.battlefield == (CardWithCounters(c),)
        assert next_state.mana_pool == Mana.from_string("")
