"""
To be run with pytest
"""

from typing import Set
from ..game_state import GameState
from ..card import Card
from ..mana import Mana


def test_play_land():
    for card_name in ["Forest", "Bojuka Bog", "Radiant Fountain"]:
        c = Card(card_name)
        state = GameState(hand=(c,), battlefield=(), land_plays_remaining=1)
        next_state = state.maybe_play_land(c).pop()
        assert next_state.battlefield == (c.with_metadata(),)
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
            mana_pool=c.casting_cost,
        )
        next_state = state.maybe_cast_spell(c).pop()
        assert next_state.hand == ()
        assert next_state.battlefield == (c.with_metadata(),)
        assert next_state.mana_pool == Mana.from_string("")


def test_pass_turn_payable_mana_debt():
    state = GameState(
        battlefield=tuple(Card("Forest").with_metadata() for _ in range(4)),
        mana_debt=Mana.from_string("2GG"),
        # So we don't fail to draw
        library=(Card("Forest"),),
    )
    next_state = state.pass_turn(99).pop()
    assert next_state.mana_pool == Mana.from_string("")


def test_pass_turn_unpayable_mana_debt():
    state = GameState(
        battlefield=(),
        # So we don't fail to draw
        library=(Card("Forest"),),
        mana_debt=Mana.from_string("2GG"),
    )
    assert not state.pass_turn(99)


def test_pass_turn_sack_saga():
    targets = (Card("Amulet of Vigor"), Card("Expedition Map"))
    state = GameState(
        battlefield=(Card("Urza's Saga").with_metadata(n_counters=2),),
        # Need two of each in our library because we draw before we search
        library=targets + targets,
    )
    next_states = state.pass_turn(99)
    assert len(next_states) == 2
    assert [len(x.battlefield) == 1 for x in next_states]
    fetched_cards = [x.battlefield[0].card for x in next_states]
    assert sorted(fetched_cards) == sorted(targets)


def test_land_plays_for_new_turn():
    azusa = Card("Azusa, Lost but Seeking").with_metadata()
    dryad = Card("Dryad of the Ilysian Grove").with_metadata()
    data_provider = [
        {"battlefield": (), "land_plays": 1},
        {"battlefield": (dryad,), "land_plays": 2},
        {"battlefield": (azusa,), "land_plays": 3},
        {"battlefield": (dryad, dryad), "land_plays": 3},
        {"battlefield": (dryad, azusa), "land_plays": 4},
        # duplicate azusa should be ignored
        {"battlefield": (dryad, azusa, azusa), "land_plays": 4},
    ]
    for data in data_provider:
        battlefield = data["battlefield"]
        land_plays = data["land_plays"]
        state = GameState(battlefield=battlefield, library=(Card("Forest"),))
        next_state = state.pass_turn(99).pop()
        assert next_state.land_plays_remaining == land_plays


def test_sack_duplicate_legendary():
    c = Card("Boseiju, Who Endures")
    state = GameState(
        hand=(c,),
        battlefield=(c.with_metadata(),),
        mana_pool=Mana.from_string(""),
        land_plays_remaining=1,
    )
    # We should keep the untapped copy
    next_state = state.maybe_play_land(c).pop()
    assert next_state.mana_pool == Mana.from_string("G")
    assert next_state.battlefield == (c.with_metadata(),)


def test_activate_expedition_map():
    max_turn = 3
    state = GameState(
        turn=max_turn,
        battlefield=(
            Card("Expedition Map").with_metadata(),
            Card("Amulet of Vigor").with_metadata(),
        ),
        land_plays_remaining=1,
        mana_pool=Mana.from_string("5G"),
        hand=(Card("Primeval Titan"),),
        library=(Card("Simic Growth Chamber"),),
    )
    # Should be three moves from completion: activate map, play SGC, cast Titan
    states = {state}
    for _ in range(3):
        new_states = set()
        for s in states:
            for ns in s.get_next_states(max_turn):
                # Drop anything that gives up by passing the turn
                if ns.turn > max_turn:
                    continue
                new_states.add(ns)
        states = new_states
    assert any(s.is_done for s in states)
