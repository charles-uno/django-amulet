"""
To be run with pytest
"""

from ..mana import Mana


def test_wrapper():
    assert Mana.from_string("2GG") == Mana(green=2, total=4)
    assert Mana.from_string("") == Mana(green=0, total=0)
    assert Mana.from_string("WUBRG") == Mana(green=1, total=5)
    assert Mana.from_string("G123G") == Mana(green=2, total=8)


def test_ge():
    assert Mana.from_string("3GG") >= Mana.from_string("1GG")
    assert Mana.from_string("3GG") >= Mana.from_string("3GG")
    # No comparison
    assert not Mana.from_string("8G") >= Mana.from_string("GG")
    assert not Mana.from_string("GG") >= Mana.from_string("8G")


def test_le():
    assert Mana.from_string("1GG") <= Mana.from_string("3GG")
    assert Mana.from_string("3GG") <= Mana.from_string("3GG")
    # No comparison
    assert not Mana.from_string("GG") <= Mana.from_string("8G")
    assert not Mana.from_string("8G") <= Mana.from_string("GG")


def test_eq():
    assert Mana.from_string("3GG") == Mana.from_string("3GG")


def test_add():
    assert Mana.from_string("2G") + Mana.from_string("1G") == Mana.from_string("3GG")


def test_sub():
    assert Mana.from_string("2G") - Mana.from_string("1G") == Mana.from_string("1")
    assert Mana.from_string("2GG") - Mana.from_string("3") == Mana.from_string("G")


def test_mul():
    assert Mana.from_string("1G") * 3 == Mana.from_string("3GGG")
    assert Mana.from_string("1G") * 0 == Mana.from_string("0")


def test_bool():
    assert bool(Mana.from_string("")) is False
    assert bool(Mana.from_string("1")) is True
