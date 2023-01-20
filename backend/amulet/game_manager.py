from typing import Tuple, List, Set

from .game_state import GameState
from .note import Note


class GameManager:
    @classmethod
    def run_from_deck_list(
        cls, deck_list: List[str], max_turn: int = 4
    ) -> Tuple[Note, ...]:
        # Draw our opening hand and pass into turn 1
        states = GameState.get_initial_state_from_deck_list(deck_list).get_next_states(
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
