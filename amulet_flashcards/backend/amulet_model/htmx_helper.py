"""
Helpers for parsing HTMX payloads into Python data structures, as well as
formatting Python data structures into HTMX
For more information on HTMX, see htmx.org
"""

import json
import math
from typing import Dict, List, Optional

from .game_state import GameSummaryDict, OpenerDict
from .game_manager import ModelInputDict, ModelOutputDict, ModelOutputDict
from .note import Note, NoteType


class Htmx(str):
    @classmethod
    def join(cls, *args: str) -> "Htmx":
        return Htmx("".join(args))


class HtmxHelper:
    @classmethod
    def format_input(cls, mid: ModelInputDict) -> Htmx:
        htmx_teaser = cls._format_teaser(mid)
        htmx_buttons = cls._format_buttons(mid)
        htmx_opener = cls._format_opener(mid["opener"])
        return Htmx.join(htmx_teaser, htmx_buttons, htmx_opener)

    @classmethod
    def _format_opener(cls, opener: OpenerDict) -> Htmx:
        card_tags = [cls._card_image(c) for c in opener["hand"]]
        htmx_cards = cls._div(
            cls._div("".join(card_tags), klass="opener-cards"), klass="cards-wrap"
        )
        return Htmx.join(htmx_cards)

    @classmethod
    def _format_buttons(cls, mid: ModelInputDict) -> Htmx:
        buttons = [
            cls._format_refresh_button(),
            cls._format_play_button(mid),
            cls._format_read_more(),
        ]
        wrapped_buttons = [
            cls._div(cls._div(b, klass="button-wrap"), klass="third-width")
            for b in buttons
        ]
        return cls._div(Htmx.join(*wrapped_buttons), klass="buttons-wrap")

    @classmethod
    def _format_read_more(cls) -> Htmx:
        return cls._tag(
            "button",
            inner_html="read more...",
            onclick="show_about()",
            id="about-button",
        )

    @classmethod
    def _format_refresh_button(cls) -> Htmx:
        return cls._tag(
            "button",
            inner_html="draw a new hand",
            **{
                "id": "opener-button",
                "hx-get": "/api/opener",
                "hx-trigger": "click",
                "hx-target": "#main",
                "hx-swap": "innerHTML",
            },
        )

    @classmethod
    def _format_play_button(cls, mid: ModelInputDict) -> Htmx:
        return cls._tag(
            "button",
            inner_html="play it out",
            **{
                "id": "play-button",
                "hx-get": "/api/play",
                "hx-trigger": "click",
                "hx-target": "#main",
                "hx-swap": "innerHTML",
                "hx-vals": cls._serialize_payload(mid),
            },
        )

    @classmethod
    def parse_payload(cls, payload: Dict[str, str]) -> ModelInputDict:
        hand = cls._deserialize_list_of_strings(payload["hand"])
        library = cls._deserialize_list_of_strings(payload["library"])
        on_the_play = cls._deserialize_bool(payload["on_the_play"])
        return {
            "opener": {
                "hand": hand,
                "library": library,
                "on_the_play": on_the_play,
            },
            "stats": cls._deserialize_stats(payload["stats"]),
        }

    @classmethod
    def format_output(cls, mod: ModelOutputDict) -> Htmx:
        # We redraw everything, so gotta include the opener here
        htmx_opener = cls.format_input({"opener": mod["opener"], "stats": mod["stats"]})
        htmx_summary = cls._format_summary(mod["summary"])
        return Htmx.join(htmx_opener, htmx_summary)

    @classmethod
    def _format_summary(cls, summary: GameSummaryDict) -> Htmx:
        # Our notes only identify the beginning of turns and lines. Tidy up the
        # end tag bookkeeping. FYI: even if we skip this step, Chrome still
        # figures it out
        htmx_summary_raw = "".join(cls._from_note(n) for n in summary["notes"])
        misplaced_tags = "</p></div>"
        htmx_summary = htmx_summary_raw[len(misplaced_tags) :] + misplaced_tags
        return cls._div(htmx_summary, klass="summary-wrap")

    @classmethod
    def _format_teaser(cls, mid: ModelInputDict) -> Htmx:
        pt = cls.card_name("Primeval Titan")
        if mid["opener"]["on_the_play"]:
            turn_order = cls._span("on the play", klass="teaser-turn-order")
            turn_3_odds = "32%"
        else:
            turn_order = cls._span("on the draw", klass="teaser-turn-order")
            turn_3_odds = "45%"
        avg_line = f"The average seven-card hand has a {turn_3_odds} chance to cast {pt} by turn three {turn_order}. "
        n_success = mid["stats"][2] + mid["stats"][3]
        n_total = sum(mid["stats"].values())
        if n_total == 0:
            data_line = "Play this hand out a few times to see how it compares!"
        elif n_success == 0:
            # If we have no successes, base uncertainty on n_failures
            r_min = 0
            r_max = 100 * math.sqrt(n_total) / n_total
            data_line = f"This hand has a {r_min:.0f}% to {r_max:.0f}% chance to do so ({n_success}/{n_total} samples)."
        else:
            r_max = 100.0 * min(1, (n_success + math.sqrt(n_success)) / n_total)
            r_min = 100.0 * max(0, (n_success - math.sqrt(n_success)) / n_total)
            data_line = f"This hand has a {r_min:.0f}% to {r_max:.0f}% chance to do so ({n_success}/{n_total} samples)."
        return cls._div(
            cls._tag("p", avg_line + data_line, klass="teaser"),
            klass="teaser-wrap",
        )

    @classmethod
    def _serialize_payload(cls, mid: ModelInputDict) -> str:
        opener = mid["opener"]
        hand_serialized = cls._serialize_list_of_strings(opener["hand"])
        library_serialized = cls._serialize_list_of_strings(opener["library"])
        otp_serialized = cls._serialize_bool(opener["on_the_play"])
        stats_serialized = cls._serialize_stats(mid["stats"])
        return json.dumps(
            {
                "hand": hand_serialized,
                "library": library_serialized,
                "on_the_play": otp_serialized,
                "stats": stats_serialized,
            }
        )

    @classmethod
    def _serialize_list_of_strings(cls, x: List[str]) -> str:
        return ";".join(x).replace("'", "&apos;")

    @classmethod
    def _deserialize_list_of_strings(cls, x: str) -> List[str]:
        return x.replace("&apos;", "'").split(";")

    @classmethod
    def _deserialize_stats(cls, x: str) -> Dict[int, int]:
        # "2,5,7,6,3" -> {1:2, 2:5, 3:7, 4:6, 5:3}
        vals = x.split(",")
        if len(vals) != 5 or not all(v.isdigit() for v in vals):
            raise ValueError(f"unable to deserialize stats from {repr(x)}")
        return {i + 1: int(v) for i, v in enumerate(vals)}

    @classmethod
    def _serialize_stats(cls, x: Dict[int, int]) -> str:
        return ",".join(str(v) for k, v in sorted(x.items()))

    @classmethod
    def _deserialize_bool(cls, x: str) -> bool:
        if x == "true":
            return True
        elif x == "false":
            return False
        else:
            raise ValueError(f"unable to get bool from {repr(x)}")

    @classmethod
    def _serialize_bool(cls, b: bool) -> str:
        return "true" if b else "false"

    @classmethod
    def _from_note(cls, n: Note) -> Htmx:
        if n.type == NoteType.TEXT:
            return cls._text(n.text)
        elif n.type == NoteType.LINE_BREAK:
            return cls._line_break()
        elif n.type == NoteType.TURN_BREAK:
            return cls._turn_break(n.text)
        elif n.type == NoteType.MANA:
            return cls._mana(n.text)
        elif n.type == NoteType.CARD:
            return cls.card_name(n.text)
        else:
            return cls._alert(n.text)

    @classmethod
    def card_name(cls, card_name: str, display: Optional[str] = None) -> Htmx:
        return cls._span(
            cls._quote_safe(display or card_name),
            klass="card-name",
            onclick=f'show_autocard("{cls._card_image_url(card_name)}")',
        )

    @classmethod
    def _card_image(cls, card_name: str) -> Htmx:
        return cls._img(klass="card", src=cls._card_image_url(card_name))

    @classmethod
    def _card_image_url(cls, card_name: str) -> str:
        return (
            "https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name="
            + cls._url_escape(card_name)
        )

    @classmethod
    def _quote_safe(cls, text: str) -> str:
        return text.replace("'", "&apos;").replace('"', "&quot;")

    @classmethod
    def _url_escape(cls, text: str) -> str:
        return text.replace("'", "&apos;").replace('"', "&quot;").replace(" ", "%20")

    @classmethod
    def _mana(cls, expr: str) -> Htmx:
        urls = [cls._mana_symbol_url(x) for x in expr]
        tags = [cls._img(klass="mana-symbol", src=url) for url in urls]
        return Htmx("".join(tags))

    @classmethod
    def _mana_symbol_url(cls, c: str) -> str:
        return f"https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&type=symbol&name={c}"

    @classmethod
    def _text(cls, text: str) -> Htmx:
        return Htmx(cls._quote_safe(text))

    @classmethod
    def _line_break(cls) -> Htmx:
        return Htmx("</p><p class='summary-line'>")

    @classmethod
    def _turn_break(cls, text: str) -> Htmx:
        return Htmx("</p></div><div class='summary-turn'><p class='summary-line'>")

    @classmethod
    def _alert(cls, text: str) -> Htmx:
        return cls._span(cls._quote_safe(text), klass="summary-alert")

    @classmethod
    def _img(cls, **kwargs: str) -> Htmx:
        return cls._tag("img", "", **kwargs)

    @classmethod
    def _span(cls, inner_html: str, **kwargs: str) -> Htmx:
        return cls._tag("span", inner_html, **kwargs)

    @classmethod
    def _div(cls, inner_html: str, **kwargs: str) -> Htmx:
        return cls._tag("div", inner_html, **kwargs)

    @classmethod
    def _tag(cls, tag_name: str, inner_html: str = "", **kwargs: str) -> Htmx:
        expr = "<" + tag_name
        for key, val in kwargs.items():
            key = key.replace("klass", "class")
            val = val.replace("'", "\\'")
            expr += f" {key}='{val}'"
        expr += ">"
        if tag_name != "img":
            expr += f"{inner_html}</{tag_name}>"
        return Htmx(expr)
