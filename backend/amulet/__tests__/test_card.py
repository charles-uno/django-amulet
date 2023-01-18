import pytest

from ..card import Card


def test_is_land():
    assert Card("Forest").is_land
    assert Card("Simic Growth Chamber").is_land


if __name__ == "__main__":
    pytest.main()
