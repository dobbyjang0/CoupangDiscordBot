from __future__ import annotations

import discord
import datetime

from .http import CoupangHTTPClient
from .goldbox import GoldBox
from .product import Product

from typing import Optional, List, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    _D = TypeVar('_D', discord.Client, discord.AutoShardedClient)

__all__ = (
    'CoupangClient',
)


class CoupangClient:

    def __init__(self, client: _D, *, secret_key: str, access_key: str):
        self._discord = client
        self.req = CoupangHTTPClient(self._discord, access_key=access_key, secret_key=secret_key)

    async def search_products(
        self,
        keyword: str,
        *,
        limit: int = 20
    ) -> Optional[List[Product]]:

        response = await self.req.search_products(keyword, limit)
        payloads = response.get("data", None)

        if not payloads:
            return None

        return [Product(payload) for payload in payloads["productData"]]

    def get_link(self, url: str):
        return self.req.convert_to_partner_link(url)

    async def fetch_gold_boxes(self):
        raw_data = await self.req.fetch_gold_boxes()

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

        return self.req.get_clicks(
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

        return self.req.get_orders(
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

        return self.req.get_cancels(
            start_date.strftime("%y%m%d"),
            end_date.strftime("%y%m%d"),
            page
        )
