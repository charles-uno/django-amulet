from enum import Enum
import json
from typing import NamedTuple, TypedDict

from . import helpers


class NoteDict(TypedDict):
    text: str
    type: str


class NoteType(Enum):
    TEXT = 1
    CARD = 2
    MANA = 3
    LINE_BREAK = 4
    TURN_BREAK = 5
    ALERT = 6


class Note(NamedTuple):
    text: str
    type: NoteType = NoteType.TEXT

    def to_dict(self) -> NoteDict:
        return {"text": self.text, "type": self.type.name}
