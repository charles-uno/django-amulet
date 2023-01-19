import random
from typing import Sequence

from .card import Card
from .cards import Cards
from .game_state import GameState


class GameStateManager:

    states = None

    def __init__(self, deck_list: Sequence[str]):
        deck_list = [Card(x) for x in deck_list]
        random.shuffle(deck_list)
        hand = Cards(deck_list[:7])
        library = Cards(deck_list[7:])

        state = GameState(
            library=library, hand=hand, on_the_play=True, notes=f"draw {hand}"
        )
        state = state.next_states().pop()
        state = state.next_states().pop()
        state = state.next_states().pop()
        state = state.next_states().pop()
        print(state.get_notes())
