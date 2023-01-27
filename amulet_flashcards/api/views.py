from typing import List
from django.http import HttpRequest, HttpResponse
from django.http.request import QueryDict

from .amulet_model import GameManager, OpenerDict
from .amulet_model.htmx_helper import HtmxHelper


def e2e(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list(deck_list)
    summary = GameManager.run_from_opener_htmx(opener)
    return HttpResponse(summary)


def opener(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list_htmx(deck_list)
    return HttpResponse(opener)


def play_it_out(request: HttpRequest) -> HttpResponse:
    opener = HtmxHelper.get_opener_from_request_payload(request.GET)
    return HttpResponse(GameManager.run_from_opener_htmx(opener))


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
