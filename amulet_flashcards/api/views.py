import json
from typing import List
from django.http import JsonResponse, HttpRequest, HttpResponse

from .amulet_model import GameManager


def json_e2e(request):
    deck_list = load_deck_list()
    summary = GameManager.run_e2e_json(deck_list)
    return JsonResponse(summary)


def htmx_e2e(request):
    deck_list = load_deck_list()
    summary = GameManager.run_e2e_htmx(deck_list)
    return HttpResponse(summary)


def htmx_opener(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list_htmx(deck_list)
    return HttpResponse(opener)


def htmx_play_it_out(request: HttpRequest) -> HttpResponse:

    print(request)
    print(request.POST)
    print(request.GET)
    print(request.body)

    payload = (
        request.body.decode("utf-8")
        .split("<span class='payload'>")[-1]
        .split("</span>")[0]
    )

    print(payload)

    return HttpResponse(GameManager.run_from_opener_htmx(json.loads(payload)))


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
