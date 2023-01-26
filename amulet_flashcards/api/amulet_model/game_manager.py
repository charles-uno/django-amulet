import random
import time
from typing import List, Set

from .game_state import GameState, GameSummaryDict, OpenerDict


class GameManager:
    @classmethod
    def run_e2e_json(cls, deck_list: List[str]) -> GameSummaryDict:
        opener = cls.get_opener_from_deck_list(deck_list)
        return cls.run_from_opener_json(opener)

    @classmethod
    def run_e2e_html(cls, deck_list: List[str]) -> str:
        opener = cls.get_opener_from_deck_list(deck_list)
        return cls.run_from_opener_html(opener)

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
    def run_from_opener_json(
        cls, opener: OpenerDict, max_turn: int = 4, max_wait_seconds: float = 3
    ) -> GameSummaryDict:
        return cls._run_from_opener(
            opener=opener, max_turn=max_turn, max_wait_seconds=max_wait_seconds
        ).get_json_summary_from_completed_game()

    @classmethod
    def run_from_opener_html(
        cls, opener: OpenerDict, max_turn: int = 4, max_wait_seconds: float = 3
    ) -> str:
        return cls._run_from_opener(
            opener=opener, max_turn=max_turn, max_wait_seconds=max_wait_seconds
        ).get_html_summary_from_completed_game()

    @classmethod
    def _run_from_opener(
        cls, opener: OpenerDict, max_turn: int = 4, max_wait_seconds: float = 3
    ) -> GameState:
        max_time = time.time() + max_wait_seconds
        # Draw our opening hand and pass into turn 1
        states = GameState.get_turn_zero_state_from_opener(opener).get_next_states(
            max_turn
        )
        for _ in range(max_turn):
            states = cls._get_next_turn(states, max_turn=max_turn, max_time=max_time)
        return states.pop()

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