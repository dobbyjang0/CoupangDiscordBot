import asyncio
import os
import json
import time
import hmac
import aiohttp
import hashlib

from .errors import Forbidden, InvalidSignature, CoupangException
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
        if response.headers['content-type'] == 'application/json':
            return json.loads(text)

    except KeyError:
        pass

    return text


class Route:
    GATEWAY_BASE = "https://api-gateway.coupang.com"
    URL_BASE = "/v2/providers/affiliate_open_api/apis/openapi/v1"

    def __init__(self, method: str, path: str, **parameters) -> None:
        self.path: str = path
        self.method = method
        url = "{}{}{}".format(self.GATEWAY_BASE, self.URL_BASE, path)

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url


class CoupangHTTPClient:

    def __init__(
            self,
            loop: Optional[asyncio.AbstractEventLoop] = None,
            connector: Optional[aiohttp.BaseConnector] = None
    ):

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()  if loop is None else loop
        self.__session: aiohttp.ClientSession = MISSING
        self.access_key: Optional[str] = None
        self.secret_key: Optional[str] = None
        self.connector = connector

    async def request(
            self,
            route: Route,
            *,
            files: Optional[Sequence] = None,
            form: Optional[Iterable[Dict[str, Any]]] = None,
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

        async with aiohttp.ClientSession().request(
                method=method,
                url=url,
                **kwargs
        ) as r:

            data = await json_or_text(r)

            if 300 > r.status >= 200:
                return data

            if r.status == 401:
                raise InvalidSignature

            raise

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

    def search_product(
            self,
            keyword: str,
            limit: int = 50
    ):

        if keyword is None:
            raise Forbidden("keyword is must be not NoneType.")

        r = Route("GET", "/products/search?keyword={keyword}&limit={limit}", keyword=keyword, limit=limit)
        return self.request(r)

    def convert_to_partner_link(self, urls: List[str]):
        r = Route("POST", "/deeplink")
        coupang_urls = {"coupangUrls": urls}

        return self.request(r, data=json.dumps(coupang_urls))
