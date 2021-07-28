from .asset import Asset


class BaseProduct:

    def __init__(self, data):
        self._update(data)

    def is_free_shipping(self) -> bool:
        return self._is_free_shipping

    def is_rocket(self) -> bool:
        return self._is_rocket

    @property
    def image(self):
        return self._image

    @property
    def image_url(self):
        return self.image.url

    def _update(self, data):
        self.rank = data["rank"]
        self.name = data["productName"]
        self.id = int(data["productId"])
        self.price = int(data["productPrice"])
        self.url = data["productUrl"]
        self._image = Asset(data["productImage"])
        self._is_rocket = data["isRocket"]
        self._is_free_shipping = data["isFreeShipping"]

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def to_dict(self):
        result = {
            "rank": self.rank,
            "isRocket": self.is_rocket(),
            "isFreeShipping": self.is_free_shipping(),
            "productId": self.id,
            "productImage": self.image_url,
            "productName": self.name,
            "productPrice": self.price,
            "productUrl": self.url
        }

        return result


class Product(BaseProduct):
    pass
