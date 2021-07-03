import asyncio
from . import http, product


class CoupangClient:

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.http = http.CoupangHTTPClient(access_key=access_key, secret_key=secret_key)

    async def search(
            self,
            keyword: str,
            limit: int = 20
    ):

        product_payload = await self.http.search_product(keyword, limit)

        return product.Product(product_payload)

    async def get_link(self, url):
        return await self.http.convert_to_partner_link([url])
