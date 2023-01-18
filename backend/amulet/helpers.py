def highlight(text: str, color: str = None) -> str:
    if color == "green":
        return "\033[32m" + text + "\033[0m"
    if color == "blue":
        return "\033[36m" + text + "\033[0m"
    if color == "brown":
        return "\033[33m" + text + "\033[0m"
    if color == "red":
        return "\033[31m" + text + "\033[0m"
    if color == "magenta":
        return "\033[0;35m" + text + "\033[0m"
    return text


def compress(text: str) -> str:
    text = text.replace("'", "").title()
    for c in "- ,.":
        text = text.replace(c, "")
    return text
