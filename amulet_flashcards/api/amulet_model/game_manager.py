import random
import time
from typing import List, Set

from .game_state import GameState, GameSummaryDict, OpenerDict
from .html_builder import HtmlBuilder, HtmlExpression


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
    def get_opener_from_deck_list_htmx(cls, deck_list: List[str]) -> HtmlExpression:
        opener = cls.get_opener_from_deck_list(deck_list)
        turn_order = "on the play" if opener["on_the_play"] else "on the draw"
        turn_order_tag = HtmlBuilder.div(turn_order, klass="opener-turn-order")
        card_tags = [HtmlBuilder.card_image(c) for c in opener["hand"]]
        cards_tag = HtmlBuilder.div("".join(card_tags), klass="opener-cards")
        # hx-vals gets confused with structured data
        hand_joined = ";".join(opener["hand"]).replace("'", "&apos;")
        library_joined = ";".join(opener["library"]).replace("'", "&apos;")
        on_the_play = "true" if opener["on_the_play"] else "false"
        play_button = HtmlBuilder.tag(
            "button",
            inner_html="play it out",
            **{
                "hx-get": "/api/play",
                "hx-trigger": "click",
                "hx-target": "#play-target",
                "hx-indicator": "#play-indicator",
                "hx-swap": "innerHTML",
                "hx-vals": f'"hand": "{hand_joined}", "library": "{library_joined}", "on_the_play": {on_the_play}',
            },
        )
        play_indicator = HtmlBuilder.div(
            "working...", id="play-indicator", klass="htmx-indicator"
        )
        play_target = HtmlBuilder.div("placeholder contents", id="play-target")

        return HtmlExpression(
            turn_order_tag + cards_tag + play_button + play_indicator + play_target
        )

    @classmethod
    def run_from_opener_htmx(
        cls, opener: OpenerDict, max_turn: int = 4, max_wait_seconds: float = 3
    ) -> HtmlExpression:
        summary = cls.run_from_opener(
            opener=opener, max_turn=max_turn, max_wait_seconds=max_wait_seconds
        )
        html_notes = [HtmlBuilder.from_note(n) for n in summary["notes"]]
        return HtmlExpression("\n".join(html_notes))

    @classmethod
    def run_from_opener(
        cls, opener: OpenerDict, max_turn: int = 4, max_wait_seconds: float = 3
    ) -> GameSummaryDict:
        # Shuffle the every time so we can play through this hand repeatedly
        random.shuffle(opener["library"])
        max_time = time.time() + max_wait_seconds
        # Draw our opening hand and pass into turn 1
        states = GameState.get_turn_zero_state_from_opener(opener).get_next_states(
            max_turn
        )
        for _ in range(max_turn):
            states = cls._get_next_turn(states, max_turn=max_turn, max_time=max_time)
        return states.pop().get_summary_from_completed_game()

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
