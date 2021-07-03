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

    @property
    def url(self):
        return self._url


