from pathlib import Path
from typing import Generator, List, Tuple
from django.http import HttpRequest, HttpResponse
import markdown

from .amulet_model import GameManager, HtmxHelper
from .amulet_model.card import Card


def e2e(request: HttpRequest) -> HttpResponse:
    deck_list = load_deck_list()
    model_input = GameManager.get_model_input_from_deck_list(deck_list)
    model_output = GameManager.run(model_input)
    return HttpResponse(HtmxHelper.format_output(model_output))


def opener(request: HttpRequest) -> HttpResponse:
    deck_list = load_deck_list()
    model_input = GameManager.get_model_input_from_deck_list(deck_list)
    return HttpResponse(HtmxHelper.format_input(model_input))


def play_it_out(request: HttpRequest) -> HttpResponse:
    model_input = HtmxHelper.parse_payload(request.GET)
    model_output = GameManager.run(model_input)
    return HttpResponse(HtmxHelper.format_output(model_output))


_BACKEND_DIR = Path(__file__).resolve().parent


def about(request: HttpRequest) -> HttpResponse:
    with open(f"{_BACKEND_DIR}/static/about.md") as handle:
        content = handle.read()

    html_content = markdown.markdown(content)
    html_content = _handle_autocard_macros(html_content)

    lands, nonlands = [], []
    for n, card_name in load_deck_list_counts():
        if Card(card_name).is_land:
            lands.append([card_name, n])
        else:
            nonlands.append([card_name, n])

    decklist = '<div class="deck-list">'
    for section_data in [nonlands, lands]:
        decklist += '<ul class="deck-section">'
        for card_name, n in sorted(section_data):
            decklist += (
                f'<li class="deck-line">{n} {HtmxHelper.card_name(card_name)}</li>'
            )
        decklist += "</ul>"
    decklist += "</div>"

    html_content = html_content.replace("$DECKLIST", decklist)

    return HttpResponse(html_content)


def _handle_autocard_macros(text):
    while "[[" in text:
        text = _handle_autocard_macro(text)
    return text


def _handle_autocard_macro(text):
    before, card_and_after = text.split("[[", 1)
    card_name, after = card_and_after.split("]]", 1)
    display = None
    if "|" in card_name:
        card_name, display = card_name.split("|", 1)
    return before + HtmxHelper.card_name(card_name, display) + after


def load_deck_list() -> List[str]:
    deck_list = []
    for n, card_name in load_deck_list_counts():
        deck_list += [card_name] * int(n)
    return deck_list


def load_deck_list_counts() -> Generator[Tuple[str, str], None, None]:
    ret = []
    with open(f"{_BACKEND_DIR}/static/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            yield tuple(line.rstrip().split(None, 1))
