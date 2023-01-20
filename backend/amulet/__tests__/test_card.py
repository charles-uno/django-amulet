import pytest

from ..card import Card
from ..mana import mana


def test_is_land():
    assert Card("Forest").is_land
    assert Card("Simic Growth Chamber").is_land


def test_taps_for():
    assert Card("Forest").taps_for == mana("G")


if __name__ == "__main__":
    pytest.main()
