"""
To be run with pytest
"""

from ..card import Card
from ..htmx_helper import HtmxHelper


def test_img():
    assert HtmxHelper._img(src="foo", klass="bar") == "<img src='foo' class='bar'>"


def test_div():
    assert (
        HtmxHelper._div("fizz", onclick="buzz()") == "<div onclick='buzz()'>fizz</div>"
    )


def test_card_name():
    # Gotta worry about escaping quotes and URL safety
    url = Card("Urza's Saga").image_url

    assert (
        HtmxHelper.card_name("Urza's Saga")
        == f"<span class='card-name' onclick='show_autocard(\"{url}\")'>Urza&apos;s Saga</span>"
    )
