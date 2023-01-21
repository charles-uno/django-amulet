"""
A GameState is an immutable object that keeps track of a single point in time
during a game. All operations (drawing a card, casting a spell, playing a land)
are handled by creating new objects. By using the GameState.get_next_states, we
iterate through all possible sequences of plays until we find a winning line.
"""

from typing import List, Sequence, Set, NamedTuple, Tuple, TypedDict

from .mana import Mana, mana
from .card import Card
from .note import Note, NoteType


class OpenerDict(TypedDict):
    hand: Sequence[str]
    library: Sequence[str]
    on_the_play: bool


class GameState(NamedTuple):
    battlefield: Tuple[Card, ...] = ()
    hand: Tuple[Card, ...] = ()
    is_done: bool = False
    land_plays_remaining: int = 0
    library: Tuple[Card, ...] = ()
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
    def get_turn_zero_state_from_opener(cls, opener: OpenerDict) -> "GameState":
        library = tuple(Card(x) for x in opener["library"])
        hand = tuple(Card(x) for x in opener["hand"])
        initial_text = "on the play" if opener["on_the_play"] else "on the draw"
        return GameState(
            library=library,
            hand=hand,
            on_the_play=opener["on_the_play"],
        ).add_notes(initial_text + " with ", hand)

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
        if self.turn < max_turn and self.should_be_abandoned_when_passing_turn():
            return set()
        # Passing the final turn means this state failed to converge. Put a
        # tombstone on it so we can still look
        if self.turn == max_turn:
            return {self.with_tombstone()}
        return {
            self.copy_with_updates(
                notes=self.notes
                + (Note("", NoteType.TURN_BREAK), Note(f"--- turn {self.turn+1}")),
                turn=self.turn + 1,
                land_plays_remaining=self.get_land_plays_for_new_turn(),
                mana_pool=mana(""),
            )
            .add_mana(self.get_mana_pool_for_new_turn())
            .pay_mana_debt()
            .draw_for_turn()
            .handle_sagas()
        }

    def draw_for_turn(self) -> "GameState":
        if self.turn == 1 and self.on_the_play:
            return self
        else:
            return self.draw_a_card()

    def should_be_abandoned_when_passing_turn(self):
        # Cast a pact we can't pay for
        mana_pool = self.get_mana_pool_for_new_turn()
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

    def with_tombstone(self) -> "GameState":
        return self.copy_with_updates(
            turn=self.turn + 1,
            notes=self.notes
            + (
                Note("", NoteType.LINE_BREAK),
                Note("FAILED TO CONVERGE", NoteType.ALERT),
            ),
        )

    def pay_mana_debt(self) -> "GameState":
        if not self.mana_debt:
            return self
        if self.mana_pool >= self.mana_debt:
            return self.add_notes(", pay for pact").pay_mana(self.mana_debt)
        raise RuntimeError(f"attempting to pay {self.mana_debt} with {self.mana_pool}")

    def get_land_plays_for_new_turn(self) -> int:
        return (
            1
            + self.battlefield.count(Card("Dryad of the Ilysian Grove"))
            + 2 * self.battlefield.count(Card("Azusa, Lost but Seeking"))
        )

    def get_mana_pool_for_new_turn(self) -> Mana:
        mana_pool = mana("")
        for c in self.battlefield:
            if c.taps_for:
                mana_pool += c.taps_for
        return mana_pool

    def handle_sagas(self) -> "GameState":
        new_battlefield = []
        note_args = []
        for c in self.battlefield:
            if not c.is_saga:
                new_battlefield.append(c)
                continue
            new_c = c.plus_counter()
            note_args += ["\n", "tick ", c, " up to ", new_c]
            # Always get Amulet
            if new_c.n_counters == 3:
                new_battlefield.append(Card("Amulet of Vigor"))
                note_args += ["\n", "sack ", new_c, ", grab ", Card("Amulet of Vigor")]
            else:
                new_battlefield.append(new_c)
        return self.copy_with_updates(battlefield=tuple(new_battlefield)).add_notes(
            *note_args
        )

    def add_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        return self.copy_with_updates(mana_pool=self.mana_pool + m).note_mana_pool()

    def pay_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        return self.copy_with_updates(mana_pool=self.mana_pool - m).note_mana_pool()

    def note_mana_pool(self) -> "GameState":
        return self.add_notes(", ", self.mana_pool, " in pool")

    def draw_a_card(self) -> "GameState":
        c = self.library[0]
        return self.copy_with_updates(
            hand=self.hand + (c,),
            library=self.library[1:],
        ).add_notes("\n", "draw ", c)

    def maybe_play_land(self, c: Card) -> Set["GameState"]:
        if c not in self.hand or not self.land_plays_remaining or not c.is_land:
            return set()
        state = self.add_land_plays(
            -1,
        ).add_notes("\n", "play ", c)
        if c.enters_tapped:
            return state.put_land_onto_battlefield_tapped(c)
        else:
            return state.put_land_onto_battlefield_untapped(c)

    def put_land_onto_battlefield_tapped(self, c: Card) -> Set["GameState"]:
        m = c.taps_for * self.battlefield.count(Card("Amulet of Vigor"))
        state = self.move_from_hand_to_battlefield(
            c,
        ).add_mana(m)
        return getattr(state, "effect_for_" + c.slug)()

    def put_land_onto_battlefield_untapped(self, c: Card) -> Set["GameState"]:
        state = self.move_from_hand_to_battlefield(
            c,
        ).add_mana(c.taps_for)
        return getattr(state, "effect_for_" + c.slug)()

    def maybe_cast_spell(self, c: Card) -> Set["GameState"]:
        if not (c in self.hand and c.is_spell and c.mana_cost <= self.mana_pool):
            return set()
        state = (
            self.move_from_hand_to_battlefield(c)
            .add_notes("\n", "cast ", c)
            .pay_mana(c.mana_cost)
        )
        return getattr(state, "effect_for_" + c.slug)()

    def move_from_hand_to_battlefield(self, c: Card) -> "GameState":
        i = self.hand.index(c)
        # When playing a saga, tick up to one counter
        c_new = c.plus_counter() if c.is_saga else c

        assert isinstance(c_new, Card)

        return self.copy_with_updates(
            hand=self.hand[:i] + self.hand[i + 1 :],
            battlefield=self.battlefield + (c_new,),
        )

    def move_from_battlefield_to_hand(self, c: Card) -> "GameState":
        i = self.battlefield.index(c)
        # When bouncing a saga, remove all counters
        return self.copy_with_updates(
            hand=self.hand + (c.without_counters(),),
            battlefield=self.battlefield[:i] + self.battlefield[i + 1 :],
        )

    def add_land_plays(self, n: int) -> "GameState":
        return self.copy_with_updates(
            land_plays_remaining=self.land_plays_remaining + n
        )

    def effect_for_amulet_of_vigor(self) -> Set["GameState"]:
        return {self}

    def effect_for_arboreal_grazer(self) -> Set["GameState"]:
        states = set()
        for c in set(self.hand):
            if not c.is_land:
                continue
            states |= self.add_notes(", into ", c).put_land_onto_battlefield_tapped(c)
        return states

    def effect_for_azusa_lost_but_seeking(
        self,
    ) -> Set["GameState"]:
        # If we just cast a duplicate Azusa, bail
        if self.battlefield.count(Card("Azusa, Lost but Seeking")) > 1:
            return set()
        return {self.add_land_plays(2)}

    def effect_for_cultivator_colossus(self) -> Set["GameState"]:
        # Don't cast unless we have at least one land in hand
        if not any(c.is_land for c in self.hand):
            return set()
        return {
            self.copy_with_updates(
                is_done=True,
            )
        }

    def effect_for_dryad_of_the_ilysian_grove(
        self,
    ) -> Set["GameState"]:
        return {self.add_land_plays(1)}

    def effect_for_explore(
        self,
    ) -> Set["GameState"]:
        return {self.add_land_plays(1).draw_a_card()}

    def effect_for_primeval_titan(
        self,
    ) -> Set["GameState"]:
        return {
            self.copy_with_updates(
                is_done=True,
            )
        }

    def effect_for_summoners_pact(
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

    def effect_for_bojuka_bog(self) -> Set["GameState"]:
        return {self}

    def effect_for_forest(self) -> Set["GameState"]:
        return {self}

    def effect_for_radiant_fountain(self) -> Set["GameState"]:
        return {self}

    def effect_for_simic_growth_chamber(self) -> Set["GameState"]:
        states = set()
        for c in set(self.battlefield):
            if c.is_land:
                states.add(
                    self.move_from_battlefield_to_hand(c).add_notes(", bounce ", c)
                )
        return states

    def effect_for_urzas_saga(self) -> Set["GameState"]:
        return {self}

    def dump(self) -> None:
        lines = [
            f"hand: {self.hand}",
            f"battlefield: {self.battlefield}",
            f"mana pool: {self.mana_pool}",
            "".join(n.get_pretty() for n in self.notes),
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

                try:
                    seq.append(tuple(sorted(val)))
                except:

                    print(val)

                    self.dump()
                    raise
            else:
                seq.append(val)
        return tuple(seq)

    def copy_with_updates(self, **kwargs) -> "GameState":
        new_kwargs = self._asdict()
        new_kwargs.update(kwargs)
        return GameState(**new_kwargs)

    def add_notes(self, *args: str | Card | Mana | Tuple[Card, ...]) -> "GameState":
        notes: List[Note] = []
        for arg in args:
            if isinstance(arg, str):
                if arg == "\n":
                    notes.append(Note("", NoteType.LINE_BREAK))
                else:
                    notes.append(Note(arg))
            elif isinstance(arg, (Card, Mana)):
                notes.extend(arg.notes)
            else:
                notes.extend(self.get_notes_for_card_tuple(arg))
        return self.copy_with_updates(notes=self.notes + tuple(notes))

    def get_notes_for_card_tuple(self, cards: Tuple[Card, ...]) -> Tuple[Note, ...]:
        notes = []
        for c in sorted(set(cards)):
            n = cards.count(c)
            if n > 1:
                notes.append(Note(str(n) + "\u00D7"))
            notes.extend(c.notes)
            notes.append(Note(" "))
        return tuple(notes[:-1])
