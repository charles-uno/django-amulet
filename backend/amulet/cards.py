from .card import Card


class Cards(tuple):
    def __add__(self, c: Card) -> "Cards":
        return Cards(self + (c,))

    def __sub__(self, c: Card) -> "Cards":
        i = self.index(c)
        return Cards(self[:i] + self[i + 1 :])
