from .product import BaseProduct

__all__ = ('GoldBox',)


class GoldBox(BaseProduct):

    def __str__(self):
        return self.name

    def __int__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, GoldBox) and self.id == other.id
