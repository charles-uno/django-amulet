from typing import List
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.http.request import QueryDict

from .amulet_model import GameManager, OpenerDict


def json_e2e(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list(deck_list)
    summary = GameManager.run_from_opener(opener)
    return JsonResponse(summary)


def htmx_e2e(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list(deck_list)
    summary = GameManager.run_from_opener_htmx(opener)
    return HttpResponse(summary)


def htmx_opener(request):
    deck_list = load_deck_list()
    opener = GameManager.get_opener_from_deck_list_htmx(deck_list)
    return HttpResponse(opener)


def htmx_play_it_out(request: HttpRequest) -> HttpResponse:
    opener = get_opener_dict_from_htmx_request(request)
    return HttpResponse(GameManager.run_from_opener_htmx(opener))


def get_opener_dict_from_htmx_request(request: HttpRequest) -> OpenerDict:
    hand = get_list_from_query_qict(request.GET, "hand")
    library = get_list_from_query_qict(request.GET, "library")
    on_the_play = get_bool_from_query_dict(request.GET, "on_the_play")
    return {
        "hand": hand,
        "library": library,
        "on_the_play": on_the_play,
    }


def get_bool_from_query_dict(qd: QueryDict, key: str) -> bool:
    val = qd.get(key)
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        raise ValueError(f"unable to get bool from {repr(val)}")


def get_list_from_query_qict(qd: QueryDict, key: str) -> List[str]:
    val = qd.get(key)
    if isinstance(val, list):
        return [str(x) for x in val]
    elif isinstance(val, str):
        # htmx gets a bit confused when you put structured data into hx-vals so
        # we just join our lists with semicolons.
        return val.split(";")
    else:
        raise ValueError(f"unable to get List[str] from {repr(val)}")


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
