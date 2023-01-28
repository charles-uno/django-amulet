"""
To be run with pytest
"""

import pytest

from ..card import Card
from ..mana import mana


def test_is_land():
    assert Card("Forest").is_land
    assert Card("Simic Growth Chamber").is_land


def test_invalid_card():
    # TODO: would be nice to raise on creation instead of on access
    with pytest.raises(ValueError):
        Card("fizz buzz").is_saga


def test_taps_for():
    assert Card("Forest").taps_for == mana("G")
