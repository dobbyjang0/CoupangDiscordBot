
class GoldBox:

    def __init__(self, data):
        self.data = data

    @property
    def product_id(self) -> int:
        return self.data["productId"]

    @property
    def product_image(self):
        return

    @property
    def product_image_url(self):
        return self.data["productImage"]

    def is_rocket(self) -> bool:
        return self.data["isRocket"]
