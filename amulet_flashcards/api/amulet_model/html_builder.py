class HtmlBuilder:
    @classmethod
    def card_name(cls, card_name: str) -> str:
        return f"<span class='summary-card' onclick='show_autocard(\"{cls.card_image_url(card_name)}\")'>{cls._quote_safe(card_name)}</span>"

    @classmethod
    def card_image(cls, card_name: str) -> str:
        return f"<img class='card' src='{cls.card_image_url(card_name)}'>"

    @classmethod
    def card_image_url(cls, card_name: str) -> str:
        return (
            "https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name="
            + cls._url_escape(card_name)
        )

    @classmethod
    def _quote_safe(cls, text: str) -> str:
        return text.replace("'", "&apos;").replace('"', "&quot;")

    @classmethod
    def _url_escape(cls, text: str) -> str:
        return text.replace("'", "&apos;").replace('"', "&quot;").replace(" ", "%20")

    @classmethod
    def mana(cls, expr: str) -> str:
        urls = [cls.mana_symbol_url(x) for x in expr]
        return "".join(f"<img class='mana-symbol' src='{url}'>" for url in urls)

    @classmethod
    def mana_symbol_url(cls, c: str) -> str:
        return f"https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&type=symbol&name={c}"

    @classmethod
    def text(cls, text: str) -> str:
        return f"<span class='summary-text'>{cls._quote_safe(text)}</span>"

    @classmethod
    def line_break(cls) -> str:
        return "<br>"

    @classmethod
    def turn_break(cls, text: str) -> str:
        return f"<br><span class='summary-text'>{cls._quote_safe(text)}</span>"

    @classmethod
    def alert(cls, text: str) -> str:
        return f"<span class='summary-alert'>{cls._quote_safe(text)}</span>"
