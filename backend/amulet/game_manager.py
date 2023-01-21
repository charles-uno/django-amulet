import random
from typing import Sequence, Tuple, List, Set, TypedDict

from .game_state import GameState, OpenerDict
from .note import Note


class GameManager:
    @classmethod
    def get_opener_from_deck_list(cls, deck_list: List[str]) -> OpenerDict:
        on_the_play = random.choice([True, False])
        random.shuffle(deck_list)
        return {
            "hand": deck_list[:7],
            "library": deck_list[7:],
            "on_the_play": on_the_play,
        }

    @classmethod
    def run_from_opener(cls, opener: OpenerDict, max_turn: int = 4) -> Sequence[Note]:
        # Draw our opening hand and pass into turn 1
        states = GameState.get_turn_zero_state_from_opener(opener).get_next_states(
            max_turn
        )
        for _ in range(max_turn):
            states = cls._get_next_turn(states, max_turn)
        return states.pop().get_notes()

    @classmethod
    def _get_next_turn(
        cls, old_states: Set[GameState], max_turn: int
    ) -> Set[GameState]:
        for s in old_states:
            if s.is_done:
                return {s}
        old_turn = max(s.get_turn() for s in old_states)
        new_states = set()
        while old_states:
            for s in old_states.pop().get_next_states(max_turn):
                if s.is_done:
                    return {s}
                elif s.get_turn() > old_turn:
                    new_states.add(s)
                else:
                    old_states.add(s)
        return new_states
