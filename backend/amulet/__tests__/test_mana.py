import pytest

from ..mana import mana, Mana


def test_wrapper():
    assert mana("2GG") == Mana(green=2, total=4)
    assert mana("") == Mana(green=0, total=0)
    assert mana("WUBRG") == Mana(green=1, total=5)
    assert mana("G123G") == Mana(green=2, total=8)


def test_ge():
    assert mana("3GG") >= mana("1GG")
    assert mana("3GG") >= mana("3GG")
    # No comparison
    assert not mana("8G") >= mana("GG")
    assert not mana("GG") >= mana("8G")


def test_le():
    assert mana("1GG") <= mana("3GG")
    assert mana("3GG") <= mana("3GG")
    # No comparison
    assert not mana("GG") <= mana("8G")
    assert not mana("8G") <= mana("GG")


def test_eq():
    assert mana("3GG") == mana("3GG")


def test_add():
    assert mana("2G") + mana("1G") == mana("3GG")


def test_sub():
    assert mana("2G") - mana("1G") == mana("1")
    assert mana("2GG") - mana("3") == mana("G")


def test_mul():
    assert mana("1G") * 3 == mana("3GGG")
    assert mana("1G") * 0 == mana("0")


if __name__ == "__main__":
    pytest.main()
