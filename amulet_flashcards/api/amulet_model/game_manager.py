"""
GameManager is a bookkeeping wrapper around GameState. It sets up the initial
state, coordinates iteration through the turns, and keeps track of cumulative
stats.
"""


import random
import time
from typing import Dict, List, Set, TypedDict

from .game_state import GameState, GameSummaryDict, OpenerDict


class ModelInputDict(TypedDict):
    opener: OpenerDict
    stats: Dict[int, int]


class ModelOutputDict(TypedDict):
    opener: OpenerDict
    summary: GameSummaryDict
    stats: Dict[int, int]


class GameManager:
    @classmethod
    def get_model_input_from_deck_list(cls, deck_list: List[str]) -> ModelInputDict:
        on_the_play = random.choice([True, False])
        random.shuffle(deck_list)
        return {
            "opener": {
                "hand": deck_list[:7],
                "library": deck_list[7:],
                "on_the_play": on_the_play,
            },
            "stats": {i: 0 for i in range(1, 6)},
        }

    @classmethod
    def run(
        cls, mid: ModelInputDict, max_turn: int = 4, max_wait_seconds: float = 3
    ) -> ModelOutputDict:
        opener = mid["opener"]
        stats = mid["stats"]
        # Shuffle the every time so we can play through this hand repeatedly
        random.shuffle(opener["library"])
        max_time = time.time() + max_wait_seconds
        # Draw our opening hand and pass into turn 1
        states = GameState.get_turn_zero_state_from_opener(opener).get_next_states(
            max_turn
        )
        for _ in range(max_turn):
            states = cls._get_next_turn(states, max_turn=max_turn, max_time=max_time)
        summary = states.pop().get_summary_from_completed_game()
        # Track failure to converge as turn 5+
        turn = summary["turn"] if summary["turn"] > 0 else 5
        stats[turn] += 1
        return {"opener": opener, "summary": summary, "stats": stats}

    @classmethod
    def _get_next_turn(
        cls, old_states: Set[GameState], max_turn: int, max_time: float
    ) -> Set[GameState]:
        # If we found a solution, we're done. Just send it back.
        for s in old_states:
            if s.is_done:
                return {s}
        # Check if we ran out of turns or time. Only perform this check at the
        # start of a new turn to make sure we have checked the previous turn
        # exhaustively
        for s in old_states:
            if s.is_failed:
                return {s}
        old_turn = max(s.turn for s in old_states)
        new_states = set()
        while old_states:
            for s in old_states.pop().get_next_states(max_turn):
                if s.is_done:
                    return {s}
                elif time.time() > max_time:
                    return {s.with_tombstone("timeout")}
                elif s.turn > old_turn:
                    new_states.add(s)
                else:
                    old_states.add(s)
        return new_states
