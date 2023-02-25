"""
A GameState is an immutable object that keeps track of a single point in time
during a game. All operations (drawing a card, casting a spell, playing a land)
are handled by creating new objects. By using the GameState.get_next_states, we
iterate through all possible sequences of plays until we find a winning line.
"""

from typing import List, Set, NamedTuple, Tuple, TypedDict
from typing_extensions import NotRequired, Unpack
import sys

from .mana import Mana
from .card import Card, CardWithCounters
from .note import Note


# Options are:
# 0: no notes from adding or paying mana
# 1: note mana pool any time it changes
# 2: note amulet triggers when playing a land tapped
_MANA_NOTE_STYLE = 2


class OpenerDict(TypedDict):
    hand: List[str]
    library: List[str]
    on_the_play: bool


class GameSummaryDict(TypedDict):
    notes: List[Note]
    turn: int


class GameStateUpdate(TypedDict):
    battlefield: NotRequired[Tuple[CardWithCounters, ...]]
    hand: NotRequired[Tuple[Card, ...]]
    is_done: NotRequired[bool]
    is_failed: NotRequired[bool]
    land_plays_remaining: NotRequired[int]
    library: NotRequired[Tuple[Card, ...]]
    mana_debt: NotRequired[Mana]
    mana_pool: NotRequired[Mana]
    notes: NotRequired[Tuple[Note, ...]]
    on_the_play: NotRequired[bool]
    turn: NotRequired[int]


class GameState(NamedTuple):
    battlefield: Tuple[CardWithCounters, ...] = ()
    hand: Tuple[Card, ...] = ()
    is_done: bool = False
    is_failed: bool = False
    land_plays_remaining: int = 0
    library: Tuple[Card, ...] = ()
    mana_debt: Mana = Mana.from_string("")
    mana_pool: Mana = Mana.from_string("")
    notes: Tuple[Note, ...] = ()
    on_the_play: bool = False
    opening_hand: Tuple[Card, ...] = ()
    opening_library: Tuple[Card, ...] = ()
    turn: int = 0

    @classmethod
    def get_turn_zero_state_from_opener(cls, opener: OpenerDict) -> "GameState":
        library = tuple(Card(x) for x in opener["library"])
        hand = tuple(Card(x) for x in opener["hand"])
        # Opening hand is displayed above. No need to spell it out
        return GameState(
            hand=hand,
            library=library,
            opening_hand=hand,
            opening_library=library,
            on_the_play=opener["on_the_play"],
        )

    def get_summary_from_completed_game(self) -> GameSummaryDict:
        if not self.is_done and not self.is_failed:
            raise ValueError("This game is still in progress!")
        return {
            "notes": list(self.notes),
            "turn": self.turn if self.is_done else -1,
        }

    def get_next_states(self, max_turn: int) -> Set["GameState"]:
        try:
            if self.is_failed:
                return set()
            if self.is_done or self.turn > max_turn:
                return {self}
            # Passing the turn is always an option
            states = self.pass_turn(max_turn)
            for c in set(self.hand):
                states |= self.maybe_play_land(c)
                states |= self.maybe_cast_spell(c)
            for cwc in set(self.battlefield):
                states |= self.maybe_activate(cwc)
            return states
        except Exception as exc:
            if "--debug" in sys.argv:
                raise
            return {self.with_tombstone(f"crash: {exc}")}

    def pass_turn(self, max_turn: int) -> Set["GameState"]:
        if self.turn < max_turn and self.should_be_abandoned_when_passing_turn():
            return set()
        # Passing the final turn means this state failed to converge. Put a
        # tombstone on it so we can still look
        if self.turn == max_turn:
            return {self.with_tombstone(f"no solution within {max_turn} turns")}
        return (
            self.copy_with_updates(
                notes=self.notes
                + (
                    Note.turn_break(),
                    Note(f"Turn {self.turn+1}"),
                ),
                turn=self.turn + 1,
                land_plays_remaining=self.get_land_plays_for_new_turn(),
                mana_pool=Mana.from_string(""),
            )
            .add_mana(self.get_mana_pool_for_new_turn())
            .pay_mana_debt()
            .draw_for_turn()
            .handle_sagas()
        )

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
        if any(self.mana_pool >= c.casting_cost for c in mandatory_spells):
            return True
        return False

    def with_tombstone(self, reason: str) -> "GameState":
        return self.copy_with_updates(
            is_failed=True,
            turn=self.turn + 1,
            notes=self.notes
            + (
                Note.line_break(),
                Note.alert(f"FAILED: {reason.upper()}"),
            ),
        )

    def pay_mana_debt(self) -> "GameState":
        if not self.mana_debt:
            return self
        if self.mana_pool >= self.mana_debt:
            return self.add_notes(", pay for pact").pay_mana(self.mana_debt)
        raise GameStateException(
            f"attempting to pay {self.mana_debt} with {self.mana_pool}"
        )

    def get_land_plays_for_new_turn(self) -> int:
        return (
            1
            + self._battlefield_count("Dryad of the Ilysian Grove")
            + 2 * min(1, self._battlefield_count("Azusa, Lost but Seeking"))
        )

    def get_mana_pool_for_new_turn(self) -> Mana:
        mana_pool = Mana.from_string("")
        for cwc in self.battlefield:
            if cwc.card.taps_for:
                mana_pool += cwc.card.taps_for
        return mana_pool

    def handle_sagas(self) -> Set["GameState"]:
        states = set()
        new_battlefield = tuple(cwc.plus_counter_if_saga() for cwc in self.battlefield)
        saga_going_off = CardWithCounters(Card("Urza's Saga"), 3)
        targets = [c for c in set(self.library) if c.is_saga_target]
        # Note: we only go out to turn 3 so only one saga can go off at a time
        assert new_battlefield.count(saga_going_off) < 2
        if saga_going_off in new_battlefield:
            for target in targets:
                states.add(
                    self.copy_with_updates(battlefield=new_battlefield)
                    .add_notes(
                        "\n",
                        "Sack ",
                        saga_going_off.card,
                        ", grab ",
                        target,
                    )
                    .remove_from_battlefield(saga_going_off)
                    .add_to_battlefield(target)
                )
            return states
        else:
            return {self.copy_with_updates(battlefield=new_battlefield)}

    def add_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        return self.copy_with_updates(mana_pool=self.mana_pool + m).note_mana_pool()

    def pay_mana(self, m: Mana) -> "GameState":
        if not m:
            return self
        return self.copy_with_updates(mana_pool=self.mana_pool - m).note_mana_pool()

    def note_mana_pool(self) -> "GameState":
        if _MANA_NOTE_STYLE == 1:
            return self.add_notes(" (mana: ", self.mana_pool, ")")
        else:
            return self

    def draw_a_card(self) -> "GameState":
        if not self.library:
            raise GameStateException("Trying to draw from an empty library")
        c = self.library[0]
        return self.copy_with_updates(
            hand=self.hand + (c,),
            library=self.library[1:],
        ).add_notes(", draw ", c)

    def maybe_play_land(self, c: Card) -> Set["GameState"]:
        if c not in self.hand or not self.land_plays_remaining or not c.is_land:
            return set()
        state = self.add_land_plays(
            -1,
        )
        if c.enters_tapped:
            return state.add_notes("\n", "Play ", c).put_land_onto_battlefield_tapped(c)
        else:
            return state.add_notes("\n", "Play ", c).put_land_onto_battlefield_untapped(
                c
            )

    def sack_duplicate_legendary_land_if_any(self) -> "GameState":
        # Note: this is called after every update, so there can be at most one
        for cwc in set(self.battlefield):
            if not cwc.card.is_legendary_land:
                continue
            if self.battlefield.count(cwc) > 1:
                return self.remove_from_battlefield(cwc).add_notes(
                    ", sack duplicate ", cwc.card
                )
        return self

    def put_land_onto_battlefield_tapped(self, c: Card) -> Set["GameState"]:
        n_amulets = self._battlefield_count("Amulet of Vigor")
        state = (
            self.move_from_hand_to_battlefield(
                c,
            )
            .add_mana(c.taps_for * n_amulets)
            .sack_duplicate_legendary_land_if_any()
        )
        if _MANA_NOTE_STYLE == 2:
            if n_amulets == 1:
                state = state.add_notes(f", trigger ", Card("Amulet of Vigor"))
            elif n_amulets > 1:
                state = state.add_notes(
                    f", trigger {n_amulets}x ", Card("Amulet of Vigor")
                )
        return getattr(state, "effect_for_" + c.slug)()

    def put_land_onto_battlefield_untapped(self, c: Card) -> Set["GameState"]:
        state = (
            self.move_from_hand_to_battlefield(
                c,
            )
            .add_mana(c.taps_for)
            .sack_duplicate_legendary_land_if_any()
        )
        return getattr(state, "effect_for_" + c.slug)()

    def maybe_cast_spell(self, c: Card) -> Set["GameState"]:
        if not (c in self.hand and c.is_spell and c.casting_cost <= self.mana_pool):
            return set()
        if c.is_legendary and self._battlefield_count(c):
            return set()
        state = (
            self.move_from_hand_to_battlefield(c)
            .add_notes("\n", "Cast ", c)
            .pay_mana(c.casting_cost)
        )
        return getattr(state, "effect_for_" + c.slug)()

    def maybe_activate(self, cwc: CardWithCounters) -> Set["GameState"]:
        return set()

    def move_from_hand_to_battlefield(self, c: Card) -> "GameState":
        return self.remove_from_hand(c).add_to_battlefield(c)

    def move_from_battlefield_to_hand(self, cwc: CardWithCounters) -> "GameState":
        i = self.battlefield.index(cwc)
        return self.remove_from_battlefield(cwc).add_to_hand(cwc.card)

    def add_to_hand(self, c: Card) -> "GameState":
        return self.copy_with_updates(hand=self.hand + (c,))

    def remove_from_hand(self, c: Card) -> "GameState":
        i = self.hand.index(c)
        return self.copy_with_updates(
            hand=self.hand[:i] + self.hand[i + 1 :],
        )

    def add_to_battlefield(self, c: Card) -> "GameState":
        return self.copy_with_updates(
            battlefield=self.battlefield
            + (CardWithCounters(c).plus_counter_if_saga(),),
        )

    def remove_from_battlefield(self, cwc: CardWithCounters) -> "GameState":
        i = self.battlefield.index(cwc)
        return self.copy_with_updates(
            battlefield=self.battlefield[:i] + self.battlefield[i + 1 :],
        )

    def _battlefield_count(self, card_name: str) -> int:
        return self.battlefield.count(CardWithCounters(Card(card_name)))

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
            states |= self.add_notes(" into ", c).put_land_onto_battlefield_tapped(c)
        return states

    def effect_for_azusa_lost_but_seeking(
        self,
    ) -> Set["GameState"]:
        # If we just cast a duplicate Azusa, bail
        if self._battlefield_count("Azusa, Lost but Seeking") > 1:
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

    def effect_for_expedition_map(self) -> Set["GameState"]:
        return {self}

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
            if not self.mana_pool >= c.casting_cost:
                continue
            # Optimization: whatever we Pact for, cast it right away
            states |= (
                self.copy_with_updates(
                    hand=self.hand + (c,),
                    mana_debt=self.mana_debt + Mana.from_string("2GG"),
                )
                .add_notes(", grab ", c)
                .maybe_cast_spell(c)
            )
        return states

    def effect_for_bojuka_bog(self) -> Set["GameState"]:
        return {self}

    def effect_for_boseiju_who_endures(self) -> Set["GameState"]:
        return {self}

    def effect_for_boros_garrison(self) -> Set["GameState"]:
        return {self}

    def effect_for_forest(self) -> Set["GameState"]:
        return {self}

    def effect_for_radiant_fountain(self) -> Set["GameState"]:
        return {self}

    def effect_for_tolaria_west(self) -> Set["GameState"]:
        return {self}

    def effect_for_valakut_the_molten_pinnacle(self) -> Set["GameState"]:
        return {self}

    def effect_for_simic_growth_chamber(self) -> Set["GameState"]:
        return self.bounce_land()

    def effect_for_selesnya_sanctuary(self) -> Set["GameState"]:
        return self.bounce_land()

    def effect_for_gruul_turf(self) -> Set["GameState"]:
        return self.bounce_land()

    def bounce_land(self) -> Set["GameState"]:
        states = set()
        for cwc in set(self.battlefield):
            if cwc.card.is_land:
                states.add(
                    self.move_from_battlefield_to_hand(cwc).add_notes(
                        ", bounce ", cwc.card
                    )
                )
        return states

    def effect_for_slayers_stronghold(self) -> Set["GameState"]:
        return {self}

    def effect_for_sunhome_fortress_of_the_legion(self) -> Set["GameState"]:
        return {self}

    def effect_for_crumbling_vestige(self) -> Set["GameState"]:
        return {self.add_mana(Mana.from_string("G"))}

    def effect_for_urzas_saga(self) -> Set["GameState"]:
        return {self}

    def dump(self) -> None:
        lines = [
            f"hand: {self.hand}",
            f"battlefield: {self.battlefield}",
            f"mana pool: {self.mana_pool}",
            "".join(n.dump() for n in self.notes),
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

    def copy_with_updates(self, **kwargs: Unpack[GameStateUpdate]) -> "GameState":
        new_kwargs = self._asdict()
        new_kwargs.update(kwargs)
        return GameState(**new_kwargs)

    def add_notes(self, *args: str | Card | Mana) -> "GameState":
        notes: List[Note] = []
        for arg in args:
            if isinstance(arg, Card):
                notes.append(Note.card(arg))
            elif isinstance(arg, str):
                if arg == "\n":
                    notes.append(Note.line_break())
                else:
                    notes.append(Note(arg))
            elif isinstance(arg, Mana):
                notes.append(Note.mana(arg))
            else:
                raise ValueError(f"unable to create Note from {arg}")
        return self.copy_with_updates(notes=self.notes + tuple(notes))


class GameStateException(RuntimeError):
    pass
