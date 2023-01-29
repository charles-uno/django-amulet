"""
Helpers for converting Python data structures into HTMX
For more information on HTMX, see htmx.org
"""

from typing import Dict, List
from .game_state import GameSummaryDict, OpenerDict
from .note import Note, NoteType


class Htmx(str):
    pass


class HtmxHelper:
    @classmethod
    def deserialize_opener_from_payload(cls, payload: Dict[str, str]) -> OpenerDict:
        hand = cls.deserialize_list_of_strings(payload["hand"])
        library = cls.deserialize_list_of_strings(payload["library"])
        on_the_play = cls.deserialize_bool(payload["on_the_play"])
        return {
            "hand": hand,
            "library": library,
            "on_the_play": on_the_play,
        }

    @classmethod
    def from_opener(cls, opener: OpenerDict) -> Htmx:
        turn_order = "on the play" if opener["on_the_play"] else "on the draw"
        turn_order_tag = cls.div(turn_order, klass="opener-turn-order")
        card_tags = [cls.card_image(c) for c in opener["hand"]]
        cards_tag = cls.div("".join(card_tags), klass="opener-cards")
        opener_serialized = cls.serialize_opener(opener)
        play_button = cls._tag(
            "button",
            inner_html="play it out",
            **{
                "hx-get": "/api/play",
                "hx-trigger": "click",
                "hx-target": "#play-target",
                "hx-swap": "innerHTML",
                "hx-vals": opener_serialized,
            },
        )
        play_target = cls.div("placeholder contents", id="play-target")
        return Htmx(turn_order_tag + cards_tag + play_button + play_target)

    @classmethod
    def serialize_opener(cls, opener: OpenerDict) -> str:
        hand_serialized = cls.serialize_list_of_strings(opener["hand"])
        library_serialized = cls.serialize_list_of_strings(opener["library"])
        otp_serialized = cls.serialize_bool(opener["on_the_play"])
        return f'"hand": "{hand_serialized}", "library": "{library_serialized}", "on_the_play": {otp_serialized}'

    @classmethod
    def serialize_list_of_strings(cls, x: List[str]) -> str:
        return ";".join(x).replace("'", "&apos;")

    @classmethod
    def deserialize_list_of_strings(cls, x: str) -> List[str]:
        return x.replace("&apos;", "'").split(";")

    @classmethod
    def deserialize_bool(cls, x: str) -> bool:
        if x == "true":
            return True
        elif x == "false":
            return False
        else:
            raise ValueError(f"unable to get bool from {repr(x)}")

    @classmethod
    def serialize_bool(cls, b: bool) -> str:
        return "true" if b else "false"

    @classmethod
    def from_play_summary(cls, summary: GameSummaryDict) -> Htmx:
        html_notes = [cls.from_note(n) for n in summary["notes"]]
        return Htmx("\n".join(html_notes))

    @classmethod
    def from_note(cls, n: Note) -> Htmx:
        if n.type == NoteType.TEXT:
            return cls.text(n.text)
        elif n.type == NoteType.LINE_BREAK:
            return cls.line_break()
        elif n.type == NoteType.TURN_BREAK:
            return cls.turn_break(n.text)
        elif n.type == NoteType.MANA:
            return cls.mana(n.text)
        elif n.type == NoteType.CARD:
            return cls.card_name(n.text)
        else:
            return cls.alert(n.text)

    @classmethod
    def card_name(cls, card_name: str) -> Htmx:
        return cls.span(
            cls._quote_safe(card_name),
            klass="card-name",
            onclick=f'show_autocard("{cls._card_image_url(card_name)}")',
        )

    @classmethod
    def card_image(cls, card_name: str) -> Htmx:
        return cls.img(klass="card", src=cls._card_image_url(card_name))

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
    def mana(cls, expr: str) -> Htmx:
        urls = [cls.mana_symbol_url(x) for x in expr]
        tags = [cls.img(klass="mana-symbol", src=url) for url in urls]
        return Htmx("".join(tags))

    @classmethod
    def mana_symbol_url(cls, c: str) -> str:
        return f"https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&type=symbol&name={c}"

    @classmethod
    def text(cls, text: str) -> Htmx:
        return cls.span(cls._quote_safe(text), klass="summary-text")

    @classmethod
    def line_break(cls) -> Htmx:
        return cls.br()

    @classmethod
    def turn_break(cls, text: str) -> Htmx:
        return Htmx(cls.br() + cls.span(cls._quote_safe(text), klass="summary-text"))

    @classmethod
    def alert(cls, text: str) -> Htmx:
        return cls.span(cls._quote_safe(text), klass="summary-alert")

    @classmethod
    def br(cls) -> Htmx:
        return Htmx(cls._tag("br"))

    @classmethod
    def img(cls, **kwargs: str) -> Htmx:
        return cls._tag("img", "", **kwargs)

    @classmethod
    def span(cls, inner_html: str, **kwargs: str) -> Htmx:
        return cls._tag("span", inner_html, **kwargs)

    @classmethod
    def div(cls, inner_html: str, **kwargs: str) -> Htmx:
        return cls._tag("div", inner_html, **kwargs)

    @classmethod
    def _tag(cls, tag_name: str, inner_html: str = "", **kwargs: str) -> Htmx:
        expr = "<" + tag_name
        for key, val in kwargs.items():
            key = key.replace("klass", "class")
            val = val.replace("'", "\\'")
            expr += f" {key}='{val}'"
        expr += ">"
        if tag_name not in ["img", "br"]:
            expr += f"{inner_html}</{tag_name}>"
        return Htmx(expr)
