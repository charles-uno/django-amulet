from typing import Sequence

from backend.amulet.game_state import GameState


class GameStateManager:

    states = None

    def __init__(self, library: Sequence[str]):
        initial_state = GameState(
            hand=library[:7], library_index=7, on_the_play=False, turn=0
        )
        # Only possible play from here is passing the turn
        self.states = initial_state.pass_turn()

    def next_turn(self):

        next_states = set()

        next_states = GameStates()
        for state in self:
            for _state in state.next_turn(**kwargs):
                if _state.overflowed:
                    return GameStates([_state])
                # As soon as we find a solution, bail.
                elif _state.done:
                    return GameStates([_state])
                else:
                    next_states.add(_state)
                # In the event of an overflow, bail. If we've got a solution,
                # report it. Otherwise, dump the longest state we have. That
                # might give us a sense for what's problematic.
                dt = time.time() - START_TIME
                if N_STATES > MAX_STATES or dt > MAX_SECONDS:
                    longest_state = max(next_states, key=len).overflow()
                    print("### OVERFLOW ###")
                    print(longest_state.report())
                    raise TooManyStates
        return next_states
