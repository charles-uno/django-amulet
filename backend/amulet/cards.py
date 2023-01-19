from .card import Card


class Cards(tuple):
    def __add__(self, c: Card) -> "Cards":
        return Cards(tuple.__add__(self, (c,)))

    def __sub__(self, c: Card) -> "Cards":
        i = self.index(c)
        return Cards(tuple.__add__(self[:i], self[i + 1 :]))

    def __str__(self) -> str:
        return " ".join(str(c) for c in self)
