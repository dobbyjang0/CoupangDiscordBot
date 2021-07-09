import asyncio
import datetime

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
        payloads = response.get("data", None)

        if not payloads:
            return None

        return [Product(payload) for payload in payloads["productData"]]

    def get_link(self, url: str):
        return self.http.convert_to_partner_link([url])

    async def fetch_gold_boxes(self):
        raw_data = await self.http.fetch_gold_boxes()

        return [GoldBox(data) for data in raw_data]

    def get_clicks(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            page: Optional[int] = None
    ):

        if start_date.date() < datetime.date(2018, 11, 1):
            raise

        if end_date.date() < start_date.date() - datetime.timedelta(days=180):
            raise

        return self.http.get_clicks(
            start_date.strftime("%y%m%d"),
            end_date.strftime("%y%m%d"),
            page
        )

    def get_orders(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            page: Optional[int] = None
    ):

        if start_date.date() < datetime.date(2018, 11, 1):
            raise

        if end_date.date() < start_date.date() - datetime.timedelta(days=180):
            raise

        return self.http.get_orders(
            start_date.strftime("%y%m%d"),
            end_date.strftime("%y%m%d"),
            page
        )

    def get_cancels(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            page: Optional[int] = None
    ):

        if start_date.date() < datetime.date(2018, 11, 1):
            raise

        if end_date.date() < start_date.date() - datetime.timedelta(days=180):
            raise

        return self.http.get_cancels(
            start_date.strftime("%y%m%d"),
            end_date.strftime("%y%m%d"),
            page
        )
