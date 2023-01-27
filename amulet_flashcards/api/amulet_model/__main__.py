from pathlib import Path
from typing import List

from .note import NoteDict
from .game_manager import GameManager
from .game_state import GameSummaryDict


# Root of the amulet_backend project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def main():
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list(deck_list)
    summary = GameManager.run_from_opener(opener)
    print_pretty(summary)


def load_deck_list() -> List[str]:
    deck_list = []
    with open(f"{BASE_DIR}/assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list


def print_pretty(summary: GameSummaryDict) -> None:
    print("".join(note_to_str(n) for n in summary["notes"]))


def note_to_str(n: NoteDict) -> str:
    if n["type"] == "TEXT":
        return n["text"]
    if n["type"] == "LINE_BREAK":
        return "\n"
    elif n["type"] == "TURN_BREAK":
        return f"\n---- " + n["text"]
    elif n["type"] == "CARD":
        return highlight(squish(n["text"]), "green")
    elif n["type"] == "MANA":
        return highlight(n["text"], "magenta")
    elif n["type"] == "ALERT":
        return highlight(n["text"], "red")
    else:
        raise ValueError(f"unexpected note type: {n['type']}")


def squish(text: str) -> str:
    text = text.replace("'", "").title()
    for c in "- ,.":
        text = text.replace(c, "")
    return text


def highlight(text: str, color: str) -> str:
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


if __name__ == "__main__":
    main()
