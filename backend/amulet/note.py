from enum import Enum
import json
from typing import NamedTuple

from . import helpers


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

    def to_json(self):
        return json.dumps(self._asdict())

    def get_pretty(self):
        if self.type == NoteType.TEXT:
            return self.text
        elif self.type == NoteType.LINE_BREAK:
            return "\n"
        elif self.type == NoteType.TURN_BREAK:
            return f"\n"
        elif self.type == NoteType.CARD:
            return helpers.highlight(helpers.squish(self.text), "green")
        elif self.type == NoteType.MANA:
            return helpers.highlight(self.text, "magenta")
        else:
            return helpers.highlight(self.text, "red")
