from __future__ import annotations

import asyncio
import os
import json
import time
import hmac
import aiohttp
import hashlib
import discord

from .errors import Forbidden, NotFound, InvalidSignature
from .utils import MISSING
from urllib.parse import quote as _uriquote
from typing import TypeVar, Optional, Any, Iterable, Dict, List, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    _D = TypeVar('_D', discord.Client, discord.AutoShardedClient)


def auth(*, method: str, url: str, secret_key: str, access_key: str):
    path, *query = url.split("?")

    os.environ["TZ"] = "GMT+0"
    datetime = time.strftime('%y%m%d')+'T'+time.strftime('%H%M%S')+'Z'
    message = datetime + method + path + (query[0] if query else "")

    signature = hmac.new(
        bytes(secret_key, "utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(access_key, datetime, signature)


async def json_or_text(response: aiohttp.ClientResponse) -> Any:
    text = await response.text(encoding='utf-8')

    try:
        if response.headers['content-type'] == 'application/json;charset=UTF-8':
            return json.loads(text)

    except KeyError:
        pass

    return text


class CoupangRoute:
    GATEWAY_BASE = "https://api-gateway.coupang.com"
    URL_BASE = "/v2/providers/affiliate_open_api/apis/openapi/v1"

    def __init__(self, method: str, path: str, **parameters) -> None:

        if parameters:
            path = path.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.path = path

        self.method = method
        self.url = "{}{}{}".format(self.GATEWAY_BASE, self.URL_BASE, path)


class CoupangHTTPClient:

    def __init__(self, _discord, *, access_key: str, secret_key: str):
        self._discord: _D = _discord
        self._access_key: str = access_key
        self._secret_key: str = secret_key

    async def request(
        self,
        route: CoupangRoute,
        **kwargs: Any
    ):

        method = route.method
        path = route.URL_BASE + route.path
        url = route.url

        authorization = auth(
            method=method,
            url=path,
            access_key=self._access_key,
            secret_key=self._secret_key
        )

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }

        kwargs['headers'] = headers

        async with self._discord.http._HTTPClient__session.request(method, url, **kwargs) as resp:
            data = await json_or_text(resp)

            return data

    def fetch_gold_boxes(self, sub_id: Optional[str] = None):
        r = CoupangRoute("GET", "/products/goldbox&subId={sub_id}", sub_id=sub_id)

        return self.request(r)

    async def fetch_gold_box(self, product_id: int):

        gold_boxes = await self.fetch_gold_boxes()

        result = next((x for x in gold_boxes["data"] if x["productId"] == product_id), None)

        if result:
            return result

        raise NotFound("gold box not found.")

    def search_products(
            self,
            keyword: str,
            limit: int = 50,
            sub_id: Optional[str] = None
    ):

        if keyword is None:
            raise Forbidden("keyword is must be not NoneType.")

        r = CoupangRoute(
            method="GET",
            path="/products/search?keyword={keyword}&limit={limit}&subId={sub_id}",
            keyword=keyword,
            limit=limit,
            sub_id=sub_id
        )

        return self.request(r)

    def convert_to_partner_link(self, *urls: str):
        r = CoupangRoute("POST", "/deeplink")
        coupang_urls = {"coupangUrls": urls}

        return self.request(r, data=json.dumps(coupang_urls))

    def get_clicks(
            self,
            start_date: str,
            end_date: str,
            page: Optional[int] = None
    ):

        r = CoupangRoute(
            "GET",
            "/reports/clicks?startDate={start_date}?endDate={end_date}?page={page}",
            start_date=start_date,
            end_date=end_date,
            page=page
        )

        return self.request(r)

    def get_orders(
            self,
            start_date: str,
            end_date: str,
            page: Optional[int] = None
    ):

        r = CoupangRoute(
            "GET",
            "/reports/orders?startDate={start_date}?endDate={end_date}?page={page}",
            start_date=start_date,
            end_date=end_date,
            page=page
        )

        return self.request(r)

    def get_cancels(
            self,
            start_date: str,
            end_date: str,
            page: Optional[int] = None
    ):

        r = CoupangRoute(
            "GET",
            "/reports/cancels?startDate={start_date}?endDate={end_date}?page={page}",
            start_date=start_date,
            end_date=end_date,
            page=page
        )

        return self.request(r)
