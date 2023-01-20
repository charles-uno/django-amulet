import random
from typing import Sequence, Set

from .card import Card
from .cards import Cards
from .game_state import GameState
from . import helpers


class GameStateManager:
    def __init__(self, deck_list: Sequence[str]):

        states = {
            GameState.get_initial_state_from_deck_list([Card(x) for x in deck_list])
        }

        for i in range(1, 5):
            states = self.get_next_turn(states)
            if i > 1 and len(states) == 1:
                break

        print(states.pop().get_notes())

    def get_next_turn(self, old_states: Set[GameState]) -> Set[GameState]:
        for s in old_states:
            if s.is_done:
                return {s}
        old_turn = max(s.get_turn() for s in old_states)
        new_states = set()
        while old_states:
            for s in old_states.pop().get_next_states():
                if s.is_done:
                    return {s}
                elif s.get_turn() > old_turn:
                    new_states.add(s)
                else:
                    old_states.add(s)
        return new_states
