import json
import aiohttp

from typing import Optional, Any, Iterable, Dict
from urllib.parse import quote as _uriquote


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

    def __init__(self, connector: Optional[aiohttp.BaseConnector] = None):
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

        async with self.__session.request(method, url, **kwargs) as r:
            data = await json_or_text(r)

            if 300 > r.status >= 200:
                return data

            raise

    async def close(self) -> None:

        if self.__session:
            await self.__session.close()
