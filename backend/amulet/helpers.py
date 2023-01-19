from typing import Sequence


def highlight(text: str, color: str = None) -> str:
    if color == "green":
        return "\033[32m" + text + "\033[0m"
    if color == "blue":
        return "\033[36m" + text + "\033[0m"
    if color == "brown":
        return "\033[33m" + text + "\033[0m"
    if color == "red":
        return "\033[31m" + text + "\033[0m"
    if color == "magenta":
        return "\033[0;35m" + text + "\033[0m"
    return text


def slugify(text: str) -> str:
    text = text.replace("'", "").lower()
    for c in "-,.":
        text = text.replace(c, "")
    return text.replace(" ", "_")


def squish(text: str) -> str:
    text = text.replace("'", "").title()
    for c in "- ,.":
        text = text.replace(c, "")
    return text


def onlyx(seq: Sequence):
    assert len(seq) == 1
    for elt in seq:
        return elt
