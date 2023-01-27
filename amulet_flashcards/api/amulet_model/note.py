from enum import Enum
from typing import NamedTuple, TypedDict

from .html_builder import HtmlBuilder


# For JSON serializability
class NoteDict(TypedDict):
    text: str
    type: str


class NoteType(Enum):
    TEXT = "TEXT"
    CARD = "CARD"
    MANA = "MANA"
    LINE_BREAK = "LINE_BREAK"
    TURN_BREAK = "TURN_BREAK"
    ALERT = "ALERT"


class Note(NamedTuple):
    text: str
    type: NoteType = NoteType.TEXT

    def dump(self) -> str:
        if self.type in [NoteType.LINE_BREAK, NoteType.TURN_BREAK]:
            return "\n"
        else:
            return self.text

    def to_dict(self) -> NoteDict:
        return {"text": self.text, "type": self.type.name}

    def to_html(self) -> str:
        if self.type == NoteType.TEXT:
            return HtmlBuilder.text(self.text)
        elif self.type == NoteType.LINE_BREAK:
            return HtmlBuilder.line_break()
        elif self.type == NoteType.TURN_BREAK:
            return HtmlBuilder.turn_break(self.text)
        elif self.type == NoteType.MANA:
            return HtmlBuilder.mana(self.text)
        elif self.type == NoteType.CARD:
            return HtmlBuilder.card_name(self.text)
        else:
            return HtmlBuilder.alert(self.text)
