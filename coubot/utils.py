from typing import List
from bs4 import BeautifulSoup
from aiohttp import ClientSession


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


async def parse(url: str) -> BeautifulSoup:

    async with ClientSession() as session, session.request(
        url=url,
        method="GET",
        headers={
            'User-Agent': 'Mozilla/5.0'
        }
    ) as resp:
        raw_data = await resp.read()

    return BeautifulSoup(raw_data, 'lxml')
