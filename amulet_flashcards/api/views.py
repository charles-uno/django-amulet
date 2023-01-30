from typing import List
from django.http import HttpRequest, HttpResponse

from .amulet_model import GameManager, HtmxHelper


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


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
