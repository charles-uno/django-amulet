from typing import Sequence

from .card import Card
from .game_state import GameState


class GameStateManager:

    states = None

    def __init__(self, deck_list: Sequence[str]):
        deck_list = tuple(Card(x) for x in deck_list)

        hand, library = deck_list[:7], deck_list[7:]

        state = GameState(library=library, hand=hand, on_the_play=True)
        state = state.next_states().pop()
        state = state.next_states().pop()
        state = state.next_states().pop()
        state = state.next_states().pop()
        print(state.get_notes())
