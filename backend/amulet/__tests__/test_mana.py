import pytest

from ..mana import mana


def test_creation():
    assert mana("2GG").name == "2GG"
    assert mana("WUBRG").name == "4G"
    assert mana("G123G").name == "6GG"
    assert mana("2GG").green == 2
    assert mana("2GG").green == 2


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
