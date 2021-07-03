
from .asset import Asset


class GoldBox:

    def __init__(self, data):
        self.data = data

    @property
    def product_id(self) -> int:
        return self.data["productId"]

    @property
    def product_image(self):
        return Asset(self.data["productImage"])

    @property
    def product_image_url(self):
        return self.product_image.url

    def is_rocket(self) -> bool:
        return self.data["isRocket"]
