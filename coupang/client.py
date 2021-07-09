import asyncio

from typing import Optional, List
from .http import CoupangHTTPClient
from .goldbox import GoldBox
from .product import Product


class CoupangClient:

    def __init__(
            self,
            *,
            loop: Optional[asyncio.AbstractEventLoop] = None
    ):

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop

        self.http = CoupangHTTPClient(loop=self.loop)

    def login(self, access_key: str, secret_key: str):

        loop = self.loop

        future = asyncio.ensure_future(
            self.http.static_login(
                access_key=access_key,
                secret_key=secret_key
            ),
            loop=loop
        )

        loop.run_until_complete(future)

    async def search_products(
            self,
            keyword: str,
            limit: int = 20
    ) -> Optional[List[Product]]:

        response = await self.http.search_products(keyword, limit)
        payloads = response["data"]["productData"]

        if not payloads:
            return None

        return [Product(payload) for payload in payloads]

    def get_link(self, url: str):
        return self.http.convert_to_partner_link([url])

    async def fetch_gold_boxes(self):
        raw_data = await self.http.fetch_gold_boxes()

        return [GoldBox(data) for data in raw_data]
