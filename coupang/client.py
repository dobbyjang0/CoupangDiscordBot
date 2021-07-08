import asyncio

from typing import Optional
from .http import CoupangHTTPClient
from . import product


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

    async def search(
            self,
            keyword: str,
            limit: int = 20
    ):

        product_payload = await self.http.search_product(keyword, limit)

        return product.Product(product_payload)

    def get_link(self, url: str):
        return self.http.convert_to_partner_link([url])
