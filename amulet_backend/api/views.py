from typing import List
from django.http import JsonResponse

from .amulet_model import GameManager


def index(request):
    deck_list = load_deck_list()
    notes = GameManager.run_e2e(deck_list)

    return JsonResponse({"notes": notes})


def load_deck_list() -> List[str]:
    deck_list = []
    with open("assets/deck-list.txt") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            n, card_name = line.rstrip().split(None, 1)
            deck_list += [card_name] * int(n)
    return deck_list
