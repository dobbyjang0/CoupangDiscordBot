from typing import List
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow


def pon_buttons() -> dict:

    buttons = [
        create_button(
            style=ButtonStyle.secondary,
            emoji="✅",
            custom_id="true_btn"
        ),
        create_button(
            style=ButtonStyle.secondary,
            emoji="❌",
            custom_id="false_btn"
        )
    ]

    return create_actionrow(*buttons)


def is_startswith_http_url(url: str, allow_https: bool = True) -> bool:

    if url.startswith("http://"):
        return True

    if allow_https is True:
        return url.startswith("https://")

    return False


def label_maker(string: str) -> str:
    split_strings: List[str] = string.split()
    list_length = len(split_strings)

    result = []
    length = 0

    for index, split_string in enumerate(split_strings, start=1):
        len_string = len(split_string)

        if list_length == index:
            result.append(split_string[:25 - length])
            return " ".join(result)

        if length >= 25:
            return " ".join(result)

        next_element = split_strings[index]

        if 25 - length - len_string > len(next_element):
            del split_strings[index]
            list_length -= 1
            text = f"{split_string} {next_element}"
            length += len(text) + 2
            result.append(text)

            continue

        return " ".join(result)

    return " ".join(result)
