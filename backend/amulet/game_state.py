"""
A GameState is an immutable object that keeps track of a single point in time
during a game. All operations (drawing a card, casting a spell, playing a land)
are handled by creating new objects. By using the GameState.get_next_states, we
iterate through all possible sequences of plays until we find a winning line.
"""

import random
from typing import List, Optional, Set, NamedTuple, Tuple

from .mana import Mana, mana
from .card import Card
from .cards import Cards
from . import helpers

# NOTE: we can probably improve performance by copying less often. Pass around
# intermediate values instead of making a new state every time we draw a card


class GameStateBase(NamedTuple):
    battlefield: Cards = Cards()
    hand: Cards = Cards()
    is_done: bool = False
    land_plays_remaining: int = 0
    library: Cards = Cards()
    mana_debt: Mana = mana("")
    mana_pool: Mana = mana("")
    notes: str = ""
    on_the_play: bool = False
    turn: int = 0

    def __hash__(self) -> int:
        return tuple.__hash__(self.get_comparable_tuple())

    def __eq__(self, other: "GameStateBase") -> bool:
        return self.get_comparable_tuple() == other.get_comparable_tuple()

    def get_comparable_tuple(self) -> Tuple:
        # Ignore notes when collapsing duplicates, and sort unordered tuples
        seq = []
        for key, val in sorted(self._asdict().items()):
            if key == "notes":
                continue
            if key in ["hand", "battlefield"]:
                seq.append(tuple(sorted(val)))
            else:
                seq.append(val)
        return tuple(seq)

    def get_notes(self):
        return self.notes

    def get_turn(self):
        return self.turn


class GameState(GameStateBase):
    @classmethod
    def get_initial_state_from_deck_list(
        cls, deck_list: List[Card], on_the_play: Optional[bool] = None
    ) -> "GameState":
        if on_the_play is None:
            on_the_play = random.choice([True, False])
        turn_order_note = "on the play" if on_the_play else "on the draw"
        random.shuffle(deck_list)
        hand = Cards(deck_list[:7])
        library = Cards(deck_list[7:])
        return GameState(
            library=library,
            hand=hand,
            on_the_play=True,
            notes=f"{turn_order_note} with {hand}",
        )

    def copy_with_updates(self, **kwargs) -> "GameState":
        new_kwargs = self._asdict()
        new_kwargs.update(kwargs)
        return GameState(**new_kwargs)

    def get_next_states(self, max_turn: int) -> Set["GameState"]:
        if self.is_done or self.turn > max_turn:
            return {self}
        # Passing the turn is always an option
        states = self.pass_turn(max_turn)
        for c in set(self.hand):
            states |= self.maybe_play_land(c)
            states |= self.maybe_cast_spell(c)
        return states

    def pass_turn(self, max_turn: int) -> Set["GameState"]:
        if self.turn < max_turn and self._should_be_abandoned():
            return set()
        # Passing the final turn means this state failed to converge
        if self.turn == max_turn:
            return {self._with_tombstone()}
        land_plays_remaining = self._get_land_plays_for_new_turn()
        mana_pool, pact_note = self._get_mana_pool_and_note_for_new_turn()
        if mana_pool is None:
            return set()
        state = self.copy_with_updates(
            notes=self.notes + f"\n---- turn {self.turn+1}{pact_note}",
            turn=self.turn + 1,
            land_plays_remaining=land_plays_remaining,
            mana_debt=mana(""),
            mana_pool=mana(""),
        ).add_mana(mana_pool)
        if state.turn > 1 or not state.on_the_play:
            return {state.draw_a_card()}
        else:
            return {state}

    def _should_be_abandoned(self):
        # Cast a Pact on turn 1
        if self.turn == 1 and self.mana_debt:
            return True
        # Skipped playing a land when there is no reason to defer. Note: this
        # does not apply to ETB tapped lands because of Amulet.
        mandatory_lands = {c for c in self.hand if c.always_play}
        if self.land_plays_remaining and mandatory_lands:
            return True
        # Skipped casting a spell when there is no reason to defer
        mandatory_spells = {c for c in self.hand if c.always_cast}
        if any(self.mana_pool >= c.mana_cost for c in mandatory_spells):
            return True
        return False

    def _with_tombstone(self) -> "GameState":
        return self.copy_with_updates(
            turn=self.turn + 1,
            notes=self.notes + "\n" + helpers.highlight("FAILED TO CONVERGE", "red"),
        )

    def _get_land_plays_for_new_turn(self) -> int:
        return (
            1
            + self.battlefield.count(Card("Dryad of the Ilysian Grove"))
            + 2 * self.battlefield.count(Card("Azusa, Lost but Seeking"))
        )

    def _get_mana_pool_and_note_for_new_turn(self) -> Tuple[Optional[Mana], str]:
        mana_pool = mana("")
        for c in self.battlefield:
            if c.taps_for:
                mana_pool += c.taps_for
        if not mana_pool >= self.mana_debt:
            return None, ""
        if self.mana_debt:
            return mana_pool - self.mana_debt, ", pay for pact"
        else:
            return mana_pool, ""

    def add_mana(self, m: Mana) -> "GameState":
        mana_pool = self.mana_pool + m
        return self.copy_with_updates(
            mana_pool=mana_pool, notes=self.notes + f", {mana_pool} in pool"
        )

    def pay_mana(self, m: Mana) -> "GameState":
        mana_pool = self.mana_pool - m
        return self.copy_with_updates(
            mana_pool=mana_pool, notes=self.notes + f", {mana_pool} in pool"
        )

    def tap(self, c: Card) -> "GameState":
        m = c.taps_for
        return self.add_mana(m) if m else self

    def tap_out(self) -> "GameState":
        m = mana("")
        for c in self.battlefield:
            if c.taps_for:
                m += c.taps_for
        return self.add_mana(m)

    def draw_a_card(self) -> "GameState":
        c = self.library[0]
        return self.copy_with_updates(
            notes=self.notes + f"\ndraw {c}",
            hand=self.hand + c,
            library=self.library[1:],
        )

    def maybe_play_land(self, c: Card) -> Set["GameState"]:
        if c not in self.hand or not self.land_plays_remaining or not c.is_land:
            return set()
        state = self.copy_with_updates(
            hand=self.hand - c,
            battlefield=self.battlefield + c,
            notes=self.notes + f"\nplay {c}",
            land_plays_remaining=self.land_plays_remaining - 1,
        )
        if c.enters_tapped:
            return state.play_land_tapped(c)
        else:
            return state.play_land_untapped(c)

    def play_land_tapped(self, c: Card) -> Set["GameState"]:
        m = c.taps_for * self.battlefield.count(Card("Amulet of Vigor"))
        state = self.add_mana(m) if m else self
        return getattr(state, "play_" + c.slug)()

    def play_land_untapped(self, c: Card) -> Set["GameState"]:
        state = self.tap(c)
        return getattr(state, "play_" + c.slug)()

    def maybe_cast_spell(self, c: Card) -> Set["GameState"]:
        if not (c in self.hand and c.is_spell and c.mana_cost <= self.mana_pool):
            return set()
        state = self.copy_with_updates(
            hand=self.hand - c,
            battlefield=self.battlefield + c,
            mana_pool=self.mana_pool - c.mana_cost,
            notes=self.notes + f"\ncast {c}",
        )
        return getattr(state, "cast_" + c.slug)()

    def cast_amulet_of_vigor(self) -> Set["GameState"]:
        return {self}

    def cast_arboreal_grazer(self) -> Set["GameState"]:
        states = set()
        for c in set(self.hand):
            if not c.is_land:
                continue
            states |= self.copy_with_updates(
                notes=self.notes + f" into {c}"
            ).play_land_tapped(c)
        return states

    def cast_azusa_lost_but_seeking(
        self,
    ) -> Set["GameState"]:
        # If we just cast a duplicate Azusa, bail
        if self.battlefield.count(Card("Azusa, Lost but Seeking")) > 1:
            return set()
        return {
            self.copy_with_updates(land_plays_remaining=self.land_plays_remaining + 2)
        }

    def cast_dryad_of_the_ilysian_grove(
        self,
    ) -> Set["GameState"]:
        return {
            self.copy_with_updates(land_plays_remaining=self.land_plays_remaining + 1)
        }

    def cast_explore(
        self,
    ) -> Set["GameState"]:
        return {
            self.copy_with_updates(
                land_plays_remaining=self.land_plays_remaining + 1
            ).draw_a_card()
        }

    def cast_primeval_titan(
        self,
    ) -> Set["GameState"]:
        return {
            self.copy_with_updates(
                is_done=True,
            )
        }

    def cast_summoners_pact(
        self,
    ) -> Set["GameState"]:
        states = set()
        for c in set(self.library):
            if not c.is_green_creature:
                continue
            # Never pact for something that we already have
            if c in self.hand:
                continue
            # Never pact for something we can't afford
            if not self.mana_pool >= c.mana_cost:
                continue
            # Optimization: whatever we Pact for, cast it right away
            states |= self.copy_with_updates(
                notes=self.notes + f", grab {c}",
                hand=self.hand + c,
                mana_debt=self.mana_debt + mana("2GG"),
            ).maybe_cast_spell(c)
        return states

    def play_bojuka_bog(self) -> Set["GameState"]:
        return {self}

    def play_forest(self) -> Set["GameState"]:
        return {self}

    def play_radiant_fountain(self) -> Set["GameState"]:
        return {self}

    def play_simic_growth_chamber(self) -> Set["GameState"]:
        states = set()
        for c in set(self.battlefield):
            if c.is_land:
                states.add(
                    self.copy_with_updates(
                        hand=self.hand + c,
                        battlefield=self.battlefield - c,
                        notes=self.notes + f", bounce {c}",
                    )
                )
        return states
