from typing import List
from django.http import JsonResponse, HttpResponse

from .amulet_model import GameManager


def json_e2e(request):
    deck_list = load_deck_list()
    summary = GameManager.run_e2e_json(deck_list)
    return JsonResponse(summary)


def html_e2e(request):
    deck_list = load_deck_list()
    summary = GameManager.run_e2e_html(deck_list)
    return HttpResponse(summary)


def html_opener(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list_html(deck_list)
    return HttpResponse(opener)


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
