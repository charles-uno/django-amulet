"""
Helpers for parsing HTMX payloads into Python data structures, as well as
formatting Python data structures into HTMX
For more information on HTMX, see htmx.org
"""

import json
from typing import Dict, List

from .game_manager import ModelInputDict, ModelOutputDict, ModelOutputDict
from .game_state import GameSummaryDict, OpenerDict
from .note import Note, NoteType


class Htmx(str):
    pass


class HtmxHelper:
    @classmethod
    def format_input(cls, mid: ModelInputDict) -> Htmx:
        opener = mid["opener"]
        turn_order = "on the play" if opener["on_the_play"] else "on the draw"
        turn_order_tag = cls._div(turn_order, klass="opener-turn-order")
        card_tags = [cls._card_image(c) for c in opener["hand"]]
        cards_tag = cls._div("".join(card_tags), klass="opener-cards")
        refresh_button = cls._tag(
            "button",
            inner_html="draw a new hand",
            **{
                "id": "opener-button",
                "hx-get": "/api/opener",
                "hx-trigger": "click",
                "hx-target": "#swap-target",
                "hx-swap": "innerHTML",
            },
        )
        play_button = cls._tag(
            "button",
            inner_html="play it out",
            **{
                "id": "play-button",
                "hx-get": "/api/play",
                "hx-trigger": "click",
                "hx-target": "#swap-target",
                "hx-swap": "innerHTML",
                "hx-vals": cls._serialize_opener_and_stats(opener, mid["stats"]),
            },
        )
        return Htmx(refresh_button + play_button + cards_tag + turn_order_tag)

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
        # Our notes only identify the beginning of turns and lines. Tidy up the
        # end tag bookkeeping. FYI: even if we skip this step, Chrome still
        # figures it out
        htmx_notes_raw = "".join(cls._from_note(n) for n in mod["summary"]["notes"])
        misplaced_tags = "</p></div>"
        htmx_notes = htmx_notes_raw[len(misplaced_tags) :] + misplaced_tags

        htmx_stats = cls._div(str(mod["stats"]))

        return Htmx(htmx_opener + htmx_notes + htmx_stats)

    @classmethod
    def _serialize_opener_and_stats(
        cls, opener: OpenerDict, stats: Dict[int, int]
    ) -> str:
        hand_serialized = cls._serialize_list_of_strings(opener["hand"])
        library_serialized = cls._serialize_list_of_strings(opener["library"])
        otp_serialized = cls._serialize_bool(opener["on_the_play"])
        stats_serialized = cls._serialize_stats(stats)
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
            return cls._card_name(n.text)
        else:
            return cls._alert(n.text)

    @classmethod
    def _card_name(cls, card_name: str) -> Htmx:
        return cls._span(
            cls._quote_safe(card_name),
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
