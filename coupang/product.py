from .asset import Asset


class BaseProduct:

    def __init__(self, data):
        self._update(data)

    def is_free_shipping(self) -> bool:
        return self._is_free_shipping

    def is_rocket(self) -> bool:
        return self._is_rocket

    def _update(self, data):
        self.name = data["productName"]
        self.id = int(data["productId"])
        self.price = int(data["productPrice"])
        self.url = data["productUrl"]
        self._image = Asset(data["productImage"])
        self._is_rocket = data["isRocket"]
        self._is_free_shipping = data["isFreeShipping"]


class Product(BaseProduct):

    @property
    def image(self):
        return self._image

    @property
    def image_url(self):
        return self.image.url
