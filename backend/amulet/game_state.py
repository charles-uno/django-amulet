"""
A GameState is an immutable object that keeps track of a single point in time
during a game. All operations (drawing a card, casting a spell, playing a land)
are handled by creating new objects. By using the GameState.get_next_states, we
iterate through all possible sequences of plays until we find a winning line.
"""

import random
from typing import List, Optional, Set, NamedTuple, Tuple

from .mana import Mana, mana
from .card import Card, Cards
from .note import Note, NoteType


class GameState(NamedTuple):
    battlefield: Cards = Cards()
    hand: Cards = Cards()
    is_done: bool = False
    land_plays_remaining: int = 0
    library: Cards = Cards()
    mana_debt: Mana = mana("")
    mana_pool: Mana = mana("")
    notes: Tuple[Note, ...] = ()
    on_the_play: bool = False
    turn: int = 0

    def get_notes(self):
        return self.notes

    def get_turn(self):
        return self.turn

    @classmethod
    def get_initial_state_from_deck_list(
        cls, deck_list: List[str], on_the_play: Optional[bool] = None
    ) -> "GameState":
        if on_the_play is None:
            on_the_play = random.choice([True, False])
        random.shuffle(deck_list)
        hand = Cards(Card(x) for x in deck_list[:7])
        library = Cards(Card(x) for x in deck_list[7:])
        initial_text = "on the play" if on_the_play else "on the draw"
        return GameState(
            library=library,
            hand=hand,
            on_the_play=True,
        )._add_notes(initial_text + " with ", hand)

    def get_next_states(self, max_turn: int) -> Set["GameState"]:
        if self.is_done or self.turn > max_turn:
            return {self}
        # Passing the turn is always an option
        states = self._pass_turn(max_turn)
        for c in set(self.hand):
            states |= self._maybe_play_land(c)
            states |= self._maybe_cast_spell(c)
        return states

    def _pass_turn(self, max_turn: int) -> Set["GameState"]:
        if self.turn < max_turn and self._should_be_abandoned_when_passing_turn():
            return set()
        # Passing the final turn means this state failed to converge. Put a
        # tombstone on it so we can still look
        if self.turn == max_turn:
            return {self._with_tombstone()}
        mana_pool = self._get_mana_pool_for_new_turn()
        notes = (Note("", NoteType.TURN_BREAK), Note(f"--- turn {self.turn+1}, "))
        return {
            self._copy_with_updates(
                notes=self.notes + notes,
                turn=self.turn + 1,
                land_plays_remaining=self._get_land_plays_for_new_turn(),
                mana_pool=mana(""),
            )
            ._add_mana(mana_pool)
            ._pay_mana_debt()
            ._draw_for_turn()
            ._handle_sagas()
        }

    def _draw_for_turn(self) -> "GameState":
        if self.turn == 1 and self.on_the_play:
            return self
        else:
            return self._draw_a_card()

    def _should_be_abandoned_when_passing_turn(self):
        # Cast a pact we can't pay for
        mana_pool = self._get_mana_pool_for_new_turn()
        if not mana_pool >= self.mana_debt:
            return True
        # Cast a Pact on turn 1
        if self.turn == 1 and self.mana_debt:
            return True
        # Skipped playing a land when there is no reason to defer. Note: this
        # does not apply to ETB tapped lands because of Amulet.
        mandatory_lands = {c for c in self.hand if c.is_land and c.never_defer}
        if self.land_plays_remaining and mandatory_lands:
            return True
        # Skipped casting a spell when there is no reason to defer
        mandatory_spells = {c for c in self.hand if c.is_spell and c.never_defer}
        if any(self.mana_pool >= c.mana_cost for c in mandatory_spells):
            return True
        return False

    def _with_tombstone(self) -> "GameState":
        return self._copy_with_updates(
            turn=self.turn + 1,
            notes=self.notes
            + (
                Note("", NoteType.LINE_BREAK),
                Note("FAILED TO CONVERGE", NoteType.ALERT),
            ),
        )

    def _pay_mana_debt(self) -> "GameState":
        if not self.mana_debt:
            return self
        if self.mana_pool >= self.mana_debt:
            return self._add_notes(", pay for pact")._pay_mana(self.mana_debt)
        raise RuntimeError(f"attempting to pay {self.mana_debt} with {self.mana_pool}")

    def _get_land_plays_for_new_turn(self) -> int:
        return (
            1
            + self.battlefield.count(Card("Dryad of the Ilysian Grove"))
            + 2 * self.battlefield.count(Card("Azusa, Lost but Seeking"))
        )

    def _get_mana_pool_for_new_turn(self) -> Mana:
        mana_pool = mana("")
        for c in self.battlefield:
            if c.taps_for:
                mana_pool += c.taps_for
        return mana_pool

    def _handle_sagas(self) -> "GameState":
        new_battlefield = []
        note_args = []
        for c in self.battlefield:
            if not c.is_saga:
                new_battlefield.append(c)
                continue
            new_c = c.plus_counter()
            note_args += ["\ntick ", c, " up to ", new_c]
            # Always get Amulet
            if new_c.n_counters == 3:
                new_battlefield.append(Card("Amulet of Vigor"))
                note_args += ["\nsack ", new_c, ", grab ", Card("Amulet of Vigor")]
            else:
                new_battlefield.append(new_c)
        return self._copy_with_updates(battlefield=Cards(new_battlefield))._add_notes(
            *note_args
        )

    def _add_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        return self._copy_with_updates(mana_pool=self.mana_pool + m)._note_mana_pool()

    def _pay_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        return self._copy_with_updates(mana_pool=self.mana_pool - m)._note_mana_pool()

    def _note_mana_pool(self) -> "GameState":
        return self._add_notes(", ", self.mana_pool, " in pool")

    def _draw_a_card(self) -> "GameState":
        c = self.library[0]
        return self._copy_with_updates(
            hand=self.hand + c,
            library=self.library[1:],
        )._add_notes("\n", "draw ", c)

    def _maybe_play_land(self, c: Card) -> Set["GameState"]:
        if c not in self.hand or not self.land_plays_remaining or not c.is_land:
            return set()
        state = self._add_land_plays(
            -1,
        )._add_notes("\n", "play ", c)
        if c.enters_tapped:
            return state._play_land_tapped(c)
        else:
            return state._play_land_untapped(c)

    def _play_land_tapped(self, c: Card) -> Set["GameState"]:
        m = c.taps_for * self.battlefield.count(Card("Amulet of Vigor"))
        state = self._move_from_hand_to_battlefield(
            c,
        )._add_mana(m)
        return getattr(state, "_play_" + c.slug)()

    def _play_land_untapped(self, c: Card) -> Set["GameState"]:
        state = self._move_from_hand_to_battlefield(
            c,
        )._add_mana(c.taps_for)
        return getattr(state, "_play_" + c.slug)()

    def _maybe_cast_spell(self, c: Card) -> Set["GameState"]:
        if not (c in self.hand and c.is_spell and c.mana_cost <= self.mana_pool):
            return set()
        state = (
            self._move_from_hand_to_battlefield(c)
            ._add_notes("\n", "cast ", c)
            ._pay_mana(c.mana_cost)
        )
        return getattr(state, "_cast_" + c.slug)()

    def _move_from_hand_to_battlefield(self, c: Card) -> "GameState":
        return self._copy_with_updates(
            hand=self.hand - c,
            battlefield=self.battlefield + c,
        )

    def _cast_amulet_of_vigor(self) -> Set["GameState"]:
        return {self}

    def _add_land_plays(self, n: int) -> "GameState":
        return self._copy_with_updates(
            land_plays_remaining=self.land_plays_remaining + n
        )

    def _cast_arboreal_grazer(self) -> Set["GameState"]:
        states = set()
        for c in set(self.hand):
            if not c.is_land:
                continue
            states |= self._add_notes(", into ", c)._play_land_tapped(c)
        return states

    def _cast_azusa_lost_but_seeking(
        self,
    ) -> Set["GameState"]:
        # If we just cast a duplicate Azusa, bail
        if self.battlefield.count(Card("Azusa, Lost but Seeking")) > 1:
            return set()
        return {self._add_land_plays(2)}

    def _cast_cultivator_colossus(self) -> Set["GameState"]:
        return {
            self._copy_with_updates(
                is_done=True,
            )
        }

    def _cast_dryad_of_the_ilysian_grove(
        self,
    ) -> Set["GameState"]:
        return {self._add_land_plays(1)}

    def _cast_explore(
        self,
    ) -> Set["GameState"]:
        return {self._add_land_plays(1)._draw_a_card()}

    def _cast_primeval_titan(
        self,
    ) -> Set["GameState"]:
        return {
            self._copy_with_updates(
                is_done=True,
            )
        }

    def _cast_summoners_pact(
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
            states |= (
                self._copy_with_updates(
                    hand=self.hand + c,
                    mana_debt=self.mana_debt + mana("2GG"),
                )
                ._add_notes(", grab ", c)
                ._maybe_cast_spell(c)
            )
        return states

    def _play_bojuka_bog(self) -> Set["GameState"]:
        return {self}

    def _play_forest(self) -> Set["GameState"]:
        return {self}

    def _play_radiant_fountain(self) -> Set["GameState"]:
        return {self}

    def _play_simic_growth_chamber(self) -> Set["GameState"]:
        states = set()
        for c in set(self.battlefield):
            if c.is_land:
                states.add(
                    self._copy_with_updates(
                        hand=self.hand + c.without_counters(),
                        battlefield=self.battlefield - c,
                    )._add_notes(", bounce ", c)
                )
        return states

    def _play_urzas_saga(self) -> Set["GameState"]:
        c = Card("Urza's Saga")
        c_new = c.plus_counter()
        return {
            self._copy_with_updates(
                battlefield=(self.battlefield - c) + c_new,
            )._add_notes(", tick up to ", c_new)
        }

    def _dump(self) -> None:
        lines = [
            f"hand: {self.hand}",
            f"battlefield: {self.battlefield}",
            f"mana pool: {self.mana_pool}",
            self.notes,
        ]
        print("\n".join(lines))

    def __hash__(self) -> int:
        return tuple.__hash__(self._get_comparable_tuple())

    def __eq__(self, other: "GameState") -> bool:
        return self._get_comparable_tuple() == other._get_comparable_tuple()

    def _get_comparable_tuple(self) -> Tuple:
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

    def _copy_with_updates(self, **kwargs) -> "GameState":
        new_kwargs = self._asdict()
        new_kwargs.update(kwargs)
        return GameState(**new_kwargs)

    def _add_notes(self, *args: str | Card | Cards | Mana) -> "GameState":
        notes: List[Note] = []
        for arg in args:
            if isinstance(arg, str):
                if arg.startswith("\n"):
                    arg = arg.lstrip("\n")
                    notes.append(Note("", NoteType.LINE_BREAK))
                if not arg:
                    continue
                notes.append(Note(arg))
            else:
                notes.extend(arg.notes)
        return self._copy_with_updates(notes=self.notes + tuple(notes))
