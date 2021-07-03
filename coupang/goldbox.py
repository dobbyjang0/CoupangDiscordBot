
from .asset import Asset


class GoldBox:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.name

    def __int__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, GoldBox) and self.id == other.id

    @property
    def id(self) -> int:
        return self.data["productId"]

    @property
    def name(self) -> str:
        return self.data["productName"]

    @property
    def price(self) -> int:
        return self.data["productPrice"]

    @property
    def url(self) -> str:
        return self.data["productUrl"]

    @property
    def image(self):
        return Asset(self.data["productImage"])

    @property
    def mage_url(self):
        return self.image.url

    def is_free_shipping(self) -> bool:
        return self.data["isFreeShipping"]

    def is_rocket(self) -> bool:
        return self.data["isRocket"]
