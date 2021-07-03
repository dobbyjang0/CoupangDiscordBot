from .product import BaseProduct


class GoldBox(BaseProduct):

    def __str__(self):
        return self.name

    def __int__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, GoldBox) and self.id == other.id

    @property
    def image(self):
        return self._image

    @property
    def image_url(self):
        return self.image.url
