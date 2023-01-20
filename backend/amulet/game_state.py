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
from .note import Note, NoteType
from . import helpers


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
        ).add_notes(initial_text + " with ", hand)

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
        if self.turn < max_turn and self._should_be_abandoned_when_passing_turn():
            return set()
        # Passing the final turn means this state failed to converge
        if self.turn == max_turn:
            return {self._with_tombstone()}
        land_plays_remaining = self._get_land_plays_for_new_turn()
        mana_pool, pact_note = self._get_mana_pool_and_note_for_new_turn()
        skip_draw = self.turn == 0 and self.on_the_play
        # null mana pool means we had pacts we couldn't pay for
        if mana_pool is None:
            return set()
        notes = (Note("", NoteType.TURN_BREAK), Note(f"--- turn {self.turn+1}, "))
        state = self.copy_with_updates(
            notes=self.notes + notes,
            turn=self.turn + 1,
            land_plays_remaining=land_plays_remaining,
            mana_debt=mana(""),
            mana_pool=mana(""),
        ).add_mana(mana_pool)
        if skip_draw:
            return {state.handle_sagas()}
        else:
            return {state.draw_a_card().handle_sagas()}

    def _should_be_abandoned_when_passing_turn(self):
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
        return self.copy_with_updates(
            turn=self.turn + 1,
            notes=self.notes
            + (
                Note("", NoteType.LINE_BREAK),
                Note("FAILED TO CONVERGE", NoteType.ALERT),
            ),
        )

    def note_mana_pool(self) -> "GameState":
        return self.add_notes(", ", self.mana_pool, " in pool")

    def add_notes(self, *args: str | Card | Cards | Mana) -> "GameState":
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
        return self.copy_with_updates(notes=self.notes + tuple(notes))

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

    def handle_sagas(self) -> "GameState":
        new_battlefield = []
        note_args = []
        for c in self.battlefield:
            if not c.is_saga:
                new_battlefield.append(c)
                continue
            new_c = c.plus_counter()
            note_args += ["\ntick ", c, " up to ", new_c]

            if new_c.n_counters == 3:
                new_battlefield.append(Card("Amulet of Vigor"))
                note_args += ["\nsack ", new_c, ", grab ", Card("Amulet of Vigor")]
            else:
                new_battlefield.append(new_c)
        return self.copy_with_updates(battlefield=Cards(new_battlefield)).add_notes(
            *note_args
        )

    def add_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        mana_pool = self.mana_pool + m
        return self.copy_with_updates(mana_pool=mana_pool).add_notes(
            ", ", mana_pool, " in pool"
        )

    def tap(self, c: Card) -> "GameState":
        m = c.taps_for
        return self.add_mana(m) if m else self

    def draw_a_card(self) -> "GameState":
        c = self.library[0]
        return self.copy_with_updates(
            hand=self.hand + c,
            library=self.library[1:],
        ).add_notes("\n", "draw ", c)

    def maybe_play_land(self, c: Card) -> Set["GameState"]:
        if c not in self.hand or not self.land_plays_remaining or not c.is_land:
            return set()

        state = self.copy_with_updates(
            land_plays_remaining=self.land_plays_remaining - 1,
        ).add_notes("\n", "play ", c)
        if c.enters_tapped:
            return state.play_land_tapped(c)
        else:
            return state.play_land_untapped(c)

    def play_land_tapped(self, c: Card) -> Set["GameState"]:
        m = c.taps_for * self.battlefield.count(Card("Amulet of Vigor"))
        state = self.copy_with_updates(
            hand=self.hand - c,
            battlefield=self.battlefield + c,
        ).add_mana(m)
        return getattr(state, "play_" + c.slug)()

    def play_land_untapped(self, c: Card) -> Set["GameState"]:
        state = self.copy_with_updates(
            hand=self.hand - c,
            battlefield=self.battlefield + c,
        ).add_mana(c.taps_for)
        return getattr(state, "play_" + c.slug)()

    def maybe_cast_spell(self, c: Card) -> Set["GameState"]:
        if not (c in self.hand and c.is_spell and c.mana_cost <= self.mana_pool):
            return set()
        mana_pool = self.mana_pool - c.mana_cost
        state = (
            self.copy_with_updates(
                hand=self.hand - c,
                battlefield=self.battlefield + c,
                mana_pool=mana_pool,
            )
            .add_notes("\n", "cast ", c)
            .note_mana_pool()
        )
        return getattr(state, "cast_" + c.slug)()

    def cast_amulet_of_vigor(self) -> Set["GameState"]:
        return {self}

    def cast_arboreal_grazer(self) -> Set["GameState"]:
        states = set()
        for c in set(self.hand):
            if not c.is_land:
                continue
            states |= self.add_notes(", into ", c).play_land_tapped(c)
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

    def cast_cultivator_colossus(self) -> Set["GameState"]:
        return {
            self.copy_with_updates(
                is_done=True,
            )
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
            states |= (
                self.copy_with_updates(
                    hand=self.hand + c,
                    mana_debt=self.mana_debt + mana("2GG"),
                )
                .add_notes(", grab ", c)
                .maybe_cast_spell(c)
            )
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
                        hand=self.hand + c.without_counters(),
                        battlefield=self.battlefield - c,
                    ).add_notes(", bounce ", c)
                )
        return states

    def play_urzas_saga(self) -> Set["GameState"]:

        c = Card("Urza's Saga")
        c_new = c.plus_counter()
        if c not in self.battlefield:
            self.dump()
            raise ValueError

        return {
            self.copy_with_updates(
                battlefield=(self.battlefield - c) + c_new,
            ).add_notes(", tick up to ", c_new)
        }

    def dump(self) -> None:
        lines = [
            f"hand: {self.hand}",
            f"battlefield: {self.battlefield}",
            f"mana pool: {self.mana_pool}",
            self.notes,
        ]
        print("\n".join(lines))

    def __hash__(self) -> int:
        return tuple.__hash__(self.get_comparable_tuple())

    def __eq__(self, other: "GameState") -> bool:
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
