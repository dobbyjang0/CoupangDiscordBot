import os
import json
import time
import hmac
import aiohttp
import hashlib

from .errors import Forbidden, InvalidSignature
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
    BASE = "https://api-gateway.coupang.com"

    def __init__(self, method: str, path: str, **parameters) -> None:
        self.path: str = path
        self.method = method
        url = "{}{}".format(self.BASE, path)

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url


class CoupangHTTPClient:

    def __init__(
            self,
            access_key: str,
            secret_key: str,
            connector: Optional[aiohttp.BaseConnector] = None
    ):

        self.access_key = access_key
        self.secret_key = secret_key
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
        path = route.path
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
        r = Route("POST", "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink")
        coupang_urls = {"coupangUrls": urls}

        return self.request(r, data=json.dumps(coupang_urls))
