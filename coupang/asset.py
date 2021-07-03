import aiohttp

from discord.errors import HTTPException


class AssetMixin:

    url: str

    async def read(self) -> bytes:

        async with aiohttp.ClientSession() as session, session.get(self.url) as resp:

            if resp.status == 200:
                return await resp.read()

            else:
                raise HTTPException(resp, 'failed to get asset')


class Asset(AssetMixin):

    def __init__(self, url):
        self._url = url

    def __str__(self):
        return self._url

    def __len(self):
        return len(self._url)

    def __eq__(self, other):
        return isinstance(other, Asset) and self._url == other._url

    def __hash__(self):
        return hash(self._url)

    @property
    def url(self):
        return self._url


