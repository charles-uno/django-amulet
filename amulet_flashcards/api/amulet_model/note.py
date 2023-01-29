from enum import Enum
from typing import NamedTuple

from .card import Card
from .mana import Mana


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

    @classmethod
    def card(cls, c: Card) -> "Note":
        return Note(c, NoteType.CARD)

    @classmethod
    def mana(cls, m: Mana) -> "Note":
        return Note(m.to_string(), NoteType.MANA)

    @classmethod
    def line_break(cls) -> "Note":
        return Note("", NoteType.LINE_BREAK)

    @classmethod
    def turn_break(cls) -> "Note":
        return Note("", NoteType.TURN_BREAK)

    @classmethod
    def alert(cls, text: str) -> "Note":
        return Note(text, NoteType.ALERT)

    def dump(self) -> str:
        if self.type in [NoteType.LINE_BREAK, NoteType.TURN_BREAK]:
            return "\n"
        else:
            return self.text
