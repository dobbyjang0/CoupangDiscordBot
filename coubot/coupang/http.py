import asyncio
import os
import json
import time
import hmac
import aiohttp
import hashlib

from .errors import Forbidden, NotFound, InvalidSignature, CoupangException
from .utils import MISSING
from urllib.parse import quote as _uriquote
from typing import Optional, Any, Iterable, Dict, List, Sequence


def auth(method, url, secret_key, access_key):
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

    def __init__(
            self,
            loop: Optional[asyncio.AbstractEventLoop] = None,
            connector: Optional[aiohttp.BaseConnector] = None
    ):

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        self.__session: aiohttp.ClientSession = MISSING
        self.access_key: Optional[str] = None
        self.secret_key: Optional[str] = None
        self.connector = connector

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
            access_key=self.access_key,
            secret_key=self.secret_key
        )

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }

        kwargs["headers"] = headers

        async with self.__session.request(
                method=method,
                url=url,
                **kwargs
        ) as r:

            data = await json_or_text(r)

            if 300 > r.status >= 200:
                return data

            if r.status == 401:
                raise InvalidSignature(r, 'Invalid Signature.')

            raise

    async def close(self) -> None:

        if self.__session:
            await self.__session.close()

    async def static_login(self, access_key: str, secret_key: str):

        self.__session = aiohttp.ClientSession(connector=self.connector)
        old_access_key, old_secret_key = self.access_key, self.secret_key

        self.access_key = access_key
        self.secret_key = secret_key

        try:
            data = await self.convert_to_partner_link([
                "https://www.coupang.com/np/search?component=&q=good&channel=user"
            ])

        except CoupangException as exc:
            self.access_key = old_access_key
            self.secret_key = old_secret_key

            if exc.status == 401:
                raise InvalidSignature(exc.response, 'Invalid Signature.') from exc

            raise

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

    def convert_to_partner_link(self, urls: List[str]):
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
