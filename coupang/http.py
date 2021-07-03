import os
import json
import time
import hmac
import aiohttp
import hashlib

from .errors import Forbidden
from urllib.parse import quote as _uriquote
from typing import Optional, Any, Iterable, Dict


def _dt():
    os.environ['TZ'] = 'GMT+0'
    return time.strftime('%y%m%d') + 'T'+time.strftime('%H%M%S') + 'Z'


def auth(
        method: str,
        access_key: str,
        secret_key: str,
        path: str,
        query: str = None
):

    dt = _dt()

    if query is not None:
        message = f"{dt}{method}{path}{query}"

    else:
        message = f"{dt}{method}{path}"

    signature = hmac.new(
        bytes(secret_key, "utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    authorization = f"""
    CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={dt}, signature={signature}
    """

    return authorization.strip()


async def json_or_text(response: aiohttp.ClientResponse) -> Any:
    text = await response.text(encoding='utf-8')

    try:
        if response.headers['content-type'] == 'application/json':
            return json.loads(text)

    except KeyError:
        pass

    return text


class Route:
    BASE = "https://api-gateway.coupang.com/v2/providers/affiliate_open_api/apis/openapi/v1/"

    def __init__(self, method: str, path: str, **parameters) -> None:
        self.path: str = path
        self.method = method
        url = f"{self.BASE}{self.path}"

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
        self.__session: Optional[aiohttp.ClientSession] = None

    def recreate(self) -> None:

        if self.__session.closed:
            self.__session = aiohttp.ClientSession(
                connector=self.connector
            )

    async def request(
            self,
            route: Route,
            *,
            files=None,
            form: Optional[Iterable[Dict[str, Any]]] = None,
            **kwargs
    ):

        method = route.method
        url = route.url

        authorization = auth(method=method, path=url, access_key=self.access_key, secret_key=self.secret_key)

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }

        kwargs["headers"] = headers

        async with self.__session.request(method, url, **kwargs) as r:
            data = await json_or_text(r)

            if 300 > r.status >= 200:
                return data

            raise

    async def close(self) -> None:

        if self.__session:
            await self.__session.close()

    def search_product(
            self,
            keyword: str,
            limit: int = 50
    ):

        if keyword is None:
            raise Forbidden("keyword is must be not NoneType.")

        r = Route("GET", "/products/search?keyword={keyword}&limit={limit}", keyword=keyword, limit=limit)
        return self.request(r)
