from typing import List
from django.http import HttpRequest, HttpResponse

from .amulet_model import GameManager

from .views_helper import get_opener_dict_from_request, load_deck_list


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
    opener = get_opener_dict_from_request(request)
    return HttpResponse(GameManager.run_from_opener_htmx(opener))
