"""
To be run with pytest
"""

import pytest

from ..card import card
from ..mana import mana


def test_is_land():
    assert card("Forest").is_land
    assert card("Simic Growth Chamber").is_land


def test_invalid_card():
    with pytest.raises(ValueError):
        card("fizz buzz")


def test_taps_for():
    assert card("Forest").taps_for == mana("G")
