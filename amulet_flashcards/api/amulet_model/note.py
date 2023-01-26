from enum import Enum
from typing import NamedTuple, TypedDict


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
        text_safe = self.text.replace("'", "&apos;").replace('"', "&quot;")
        if self.type == NoteType.TEXT:
            return f"<span class='summary-text'>{text_safe}</span>"
        elif self.type == NoteType.LINE_BREAK:
            return f"<br>"
        elif self.type == NoteType.TURN_BREAK:
            return f"<br><span class='summary-text'>{self.text}</span>"
        elif self.type == NoteType.MANA:
            return f"<span class='summary-mana'>{self.get_inner_html_mana()}</span>"
        elif self.type == NoteType.CARD:
            return f"<span class='summary-card' onclick='show_autocard(\"{self.get_card_image_url()}\")'>{text_safe}</span>"
        else:
            return f"<span class='summary-alert'>{text_safe}</span>"

    def get_inner_html_mana(self) -> str:
        urls = []
        for c in self.text:
            urls.append(
                f"https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&type=symbol&name={c}"
            )
        tags = [f"<img class='mana-symbol' src='{url}'>" for url in urls]
        return "".join(tags)

    def get_card_image_url(self) -> str:
        text_safe = (
            self.text.replace("'", "&apos;").replace('"', "&quot;").replace(" ", "%20")
        )
        return (
            "https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name="
            + text_safe
        )
