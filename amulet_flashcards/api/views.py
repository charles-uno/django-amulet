from typing import List
from django.http import HttpRequest, HttpResponse

from .amulet_model import GameManager, HtmxHelper


def e2e(request: HttpRequest) -> HttpResponse:
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list(deck_list)
    summary = GameManager.run_from_opener(opener)
    return HttpResponse(HtmxHelper.from_play_summary(summary))


def opener(request: HttpRequest) -> HttpResponse:
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list(deck_list)
    return HttpResponse(HtmxHelper.from_opener(opener))


def play_it_out(request: HttpRequest) -> HttpResponse:
    opener = HtmxHelper.deserialize_opener_from_payload(request.GET)
    summary = GameManager.run_from_opener(opener)
    return HttpResponse(HtmxHelper.from_play_summary(summary))


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
