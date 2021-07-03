import bs4
import aiohttp

from typing import Union


class Router:

    async def requests(
            self, method: str, url: str, header: dict = None
    ) -> Union[bs4.BeautifulSoup, dict]:

        async with aiohttp.ClientSession() as session, session.request(
                method, url, headers=header
        ) as resp:

            if resp.content_type == "application/json":
                data = await resp.json()

            else:
                raw_data = await resp.read()
                data = bs4.BeautifulSoup(raw_data, features="html.parser")

            if resp.status == 200:
                return data

            raise

    async def get(
            self, url: str, header: dict = None
    ) -> Union[bs4.BeautifulSoup, dict]:
        return await self.requests(method="GET", url=url, header=header)

    async def post(
            self, url: str, header: dict = None
    ) -> Union[bs4.BeautifulSoup, dict]:
        return await self.requests(method="POST", url=url, header=header)


class Client:

    def __init__(self):
        self.session = Router()

    async def parse(self, url: str) -> Union[bs4.BeautifulSoup, dict]:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/89.0.4389.82 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        return await self.session.get(url=url, header=header)
