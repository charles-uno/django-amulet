from pathlib import Path
from typing import List

from .note import Note, NoteType
from .game_manager import GameManager
from .game_state import GameSummaryDict, OpenerDict


_BACKEND_DIR = Path(__file__).resolve().parent.parent


def main():
    deck_list = load_deck_list()
    model_input = GameManager.get_model_input_from_deck_list(deck_list)
    model_output = GameManager.run(model_input)
    print_pretty_opener(model_input["opener"])
    print_pretty_summary(model_output["summary"])


def load_deck_list() -> List[str]:
    deck_list = []
    with open(f"{_BACKEND_DIR}/static/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list


def print_pretty_opener(opener: OpenerDict) -> None:
    print("On the play" if opener["on_the_play"] else "On the draw")
    cards = [pretty_card(c) for c in opener["hand"]]
    print("Opening hand:", *cards)


def print_pretty_summary(summary: GameSummaryDict) -> None:
    pretty_summary = "".join(note_to_str(n) for n in summary["notes"])
    print(pretty_summary.lstrip())


def note_to_str(n: Note) -> str:
    if n.type == NoteType.TEXT:
        return n.text
    if n.type == NoteType.LINE_BREAK:
        return "\n"
    elif n.type == NoteType.TURN_BREAK:
        return f"\n---- " + n.text
    elif n.type == NoteType.CARD:
        return pretty_card(n.text)
    elif n.type == NoteType.MANA:
        return highlight(n.text, "magenta")
    elif n.type == NoteType.ALERT:
        return highlight(n.text, "red")
    else:
        raise ValueError(f"unexpected note type: {n.type}")


def pretty_card(card_name: str) -> str:
    return highlight(squish(card_name), "green")


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
