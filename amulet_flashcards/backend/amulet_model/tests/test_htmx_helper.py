"""
To be run with pytest
"""

from ..htmx_helper import HtmxHelper


def test_img():
    assert HtmxHelper._img(src="foo", klass="bar") == "<img src='foo' class='bar'>"


def test_div():
    assert (
        HtmxHelper._div("fizz", onclick="buzz()") == "<div onclick='buzz()'>fizz</div>"
    )


def test_card_name():
    # Gotta worry about escaping quotes and URL safety
    assert (
        HtmxHelper._card_name("Urza's Saga")
        == "<span class='card-name' onclick='show_autocard(\"https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name=Urza&apos;s%20Saga\")'>Urza&apos;s Saga</span>"
    )