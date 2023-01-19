"""
A GameState is an immutable object that keeps track of a single point in time
during a game. All operations (drawing a card, casting a spell, playing a land)
are handled by creating new objects. By using the GameState.next_states and
GameState.next_turn, we iterate through all possible sequences of plays until
we find a winning line.
"""

from typing import Set

from .mana import Mana
from .card import Card
from .cards import Cards


from typing import NamedTuple


class GameStateBase(NamedTuple):
    battlefield: Cards = Cards()
    hand: Cards = Cards()
    is_done: bool = False
    land_plays_remaining: int = 0
    library: Cards = Cards()
    mana_pool: Mana = Mana()
    notes: str = ""
    on_the_play: bool = False
    turn: int = 0

    def __hash__(self) -> int:
        # Ignore notes when collapsing duplicates
        fields = []
        for key, val in sorted(self._asdict().items()):
            if key == "notes":
                continue
            fields.append(val)
        return tuple.__hash__(tuple(fields))

    def __eq__(self, other: "GameStateBase") -> bool:
        for key, val in sorted(self._asdict().items()):
            if key == "notes":
                continue
            if other[key] != val:
                return False
        return True


class GameState(GameStateBase):
    def _copy_with_updates(self, **kwargs) -> "GameState":
        new_kwargs = self._asdict()
        new_kwargs.update(kwargs)
        return GameState(**new_kwargs)

    def next_states(self, max_turns: int = 10) -> Set["GameState"]:
        if self.is_done:
            return {self}
        states = set()
        if self.turn != max_turns:
            states |= self.pass_turn()
        for card in set(self.hand):
            states |= self.maybe_play_land(card)
        return states

    def get_notes(self):
        return self.notes

    def pass_turn(self) -> Set["GameState"]:
        turn = self.turn + 1
        note = f"\nturn {turn}"
        if self.on_the_play and self.turn == 0:
            library = self.library
            hand = self.hand
        else:
            c = self.library[0]
            library = self.library[1:]
            hand = self.hand + c
            note += f", draw {c}"
        # Always tap out mmediately
        mana_pool = Mana()
        for c in self.battlefield:
            if c.taps_for:
                mana_pool = mana_pool + c.taps_for
        if mana_pool:
            note += f", {mana_pool} in pool"
        return {
            self._copy_with_updates(
                land_plays_remaining=1,
                mana_pool=mana_pool,
                turn=turn,
                notes=self.notes + note,
                hand=hand,
                library=library,
            )
        }

    def maybe_cast_spell(self, c: Card) -> Set["GameState"]:
        if (
            c not in self.hand
            or not c.is_spell
            or c.cost is None
            or c.cost > self.mana_pool
        ):
            return set()
        state = self._copy_with_updates(
            hand=self.hand - c,
            notes=self.notes + f"\ncast {c}",
        ).pay_mana(c.cost)
        return getattr(state, "_cast_" + c.slug)()

    def maybe_play_land(self, c: Card) -> Set["GameState"]:
        if c not in self.hand or not self.land_plays_remaining or not c.is_land:
            return set()
        state = self._copy_with_updates(
            notes=self.notes + f"\nplay {c}",
            land_plays_remaining=self.land_plays_remaining - 1,
        )
        if c.enters_tapped:
            return state.play_land_tapped(c)
        else:
            return state.play_land_untapped(c)

    def play_land_tapped(self, c: Card) -> Set["GameState"]:
        state = self._copy_with_updates(
            battlefield=self.battlefield + c,
            hand=self.hand - c,
        )
        for _ in range(self.battlefield.count("Amulet of Vigor")):
            state = state.tap(c)
        return getattr(state, "_play_" + c.slug)()

    def play_land_untapped(self, c: Card) -> Set["GameState"]:
        state = self._copy_with_updates(
            hand=self.hand - c,
            battlefield=self.battlefield + c,
        ).tap(c)
        return getattr(state, "_play_" + c.slug)()

    def tap(self, c: Card) -> "GameState":
        return self.add_mana(c.taps_for)

    def tap_out(self) -> "GameState":
        mana_to_add = Mana()
        for c in self.battlefield:
            mana_to_add += c.taps_for or ""
        return self.add_mana(mana_to_add)

    def pay_mana(self, m: Mana) -> "GameState":
        mana_pool = self.mana_pool - m
        note = f", {mana_pool} in pool"
        return self._copy_with_updates(mana_pool=mana_pool, notes=self.notes + note)

    def add_mana(self, m):
        mana_pool = self.mana_pool + m
        note = f", {mana_pool} in pool"
        return self._copy_with_updates(mana_pool=mana_pool, notes=self.notes + note)

    def _cast_primeval_titan(self) -> Set["GameState"]:
        return self._copy_with_updates(is_done=True)

    def _play_forest(self) -> Set["GameState"]:
        return {self}
