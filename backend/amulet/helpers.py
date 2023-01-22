from typing import Sequence


def slugify(text: str) -> str:
    text = text.replace("'", "").lower()
    for c in "-,.":
        text = text.replace(c, "")
    return text.replace(" ", "_")


def onlyx(seq: Sequence):
    assert len(seq) == 1
    for elt in seq:
        return elt
