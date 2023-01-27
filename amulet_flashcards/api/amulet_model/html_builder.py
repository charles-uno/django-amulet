class HtmlExpression(str):
    def __new__(cls, expr: str) -> "HtmlExpression":
        # Sanity check. Just make sure the braces match up
        braces = []
        for x in expr:
            if x == "<":
                braces.append("<")
            elif x == ">" and braces:
                braces.pop()
            elif x == ">":
                raise ValueError(f"mismatched braces in {repr(expr)}")
        return super().__new__(HtmlExpression, expr)


class HtmlBuilder:
    @classmethod
    def card_name(cls, card_name: str) -> HtmlExpression:
        return cls.span(
            cls._quote_safe(card_name),
            klass="card-name",
            onclick=f'show_autocard("{cls.card_image_url(card_name)}")',
        )

    @classmethod
    def card_image(cls, card_name: str) -> HtmlExpression:
        return cls.img(klass="card", src=cls.card_image_url(card_name))

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
    def mana(cls, expr: str) -> HtmlExpression:
        urls = [cls.mana_symbol_url(x) for x in expr]
        tags = [cls.img(klass="mana-symbol", src=url) for url in urls]
        return HtmlExpression("".join(tags))

    @classmethod
    def mana_symbol_url(cls, c: str) -> str:
        return f"https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&type=symbol&name={c}"

    @classmethod
    def text(cls, text: str) -> HtmlExpression:
        return cls.span(cls._quote_safe(text), klass="summary-text")

    @classmethod
    def line_break(cls) -> HtmlExpression:
        return cls.tag("br")

    @classmethod
    def turn_break(cls, text: str) -> HtmlExpression:
        return HtmlExpression(
            cls.tag("br") + cls.span(cls._quote_safe(text), klass="summary-text")
        )

    @classmethod
    def alert(cls, text: str) -> HtmlExpression:
        return cls.span(cls._quote_safe(text), klass="summary-alert")

    @classmethod
    def img(cls, **kwargs: str) -> HtmlExpression:
        return cls.tag("img", "", **kwargs)

    @classmethod
    def span(cls, inner_html: str, **kwargs: str) -> HtmlExpression:
        return cls.tag("span", inner_html, **kwargs)

    @classmethod
    def div(cls, inner_html: str, **kwargs: str) -> HtmlExpression:
        return cls.tag("div", inner_html, **kwargs)

    @classmethod
    def tag(cls, tag_name: str, inner_html: str = "", **kwargs: str) -> HtmlExpression:
        expr = "<" + tag_name
        for key, val in kwargs.items():
            key = key.replace("klass", "class")
            val = val.replace("'", "\\'")
            expr += f" {key}='{val}'"
        expr += ">"
        if tag_name not in ["img", "br"]:
            expr += f"{inner_html}</{tag_name}>"
        return HtmlExpression(expr)
