from typing import TypeVar
from discord import Colour as DiscordColour

CT = TypeVar('CT', bound='Colour')

__all__ = (
    'Colour',
    'Color',
)


class Colour(DiscordColour):

    @classmethod
    def warning(cls) -> CT:
        return cls(0xf9c704)


Color = Colour
