import pytest

from ..mana import Mana


def test_creation():
    assert Mana("2GG").name == "2GG"
    assert Mana("WUBRG").name == "4G"
    assert Mana("G123G").name == "6GG"
    assert Mana("2GG").green == 2
    assert Mana("2GG").green == 2


def test_ge():
    assert Mana("3GG") >= Mana("1GG")
    assert Mana("3GG") >= Mana("3GG")
    # No comparison
    assert not Mana("8G") >= Mana("GG")
    assert not Mana("GG") >= Mana("8G")


def test_le():
    assert Mana("1GG") <= Mana("3GG")
    assert Mana("3GG") <= Mana("3GG")
    # No comparison
    assert not Mana("GG") <= Mana("8G")
    assert not Mana("8G") <= Mana("GG")


def test_eq():
    assert Mana("3GG") == Mana("3GG")


def test_add():
    assert Mana("2G") + Mana("1G") == Mana("3GG")


def test_sub():
    assert Mana("2G") - Mana("1G") == Mana("1")
    assert Mana("2GG") - Mana("3") == Mana("G")


def test_mul():
    assert Mana("1G") * 3 == Mana("3GGG")
    assert Mana("1G") * 0 == Mana("0")


if __name__ == "__main__":
    pytest.main()
