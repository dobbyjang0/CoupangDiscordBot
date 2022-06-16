from __future__ import annotations

import sys

from discord import Embed
from typing import Any, Union, Type, TypeVar, TYPE_CHECKING

from .errors import NoneFormName

if TYPE_CHECKING:
    E = TypeVar('E', bound='Embed')

__all__ = (
    'EmbedForms',
)


def embed_factory(form_name, *arg, **kwargs):

    if hasattr(sys.modules[__name__], form_name):
        return getattr(sys.modules[__name__], form_name)(*arg, **kwargs)

    raise NoneFormName(form_name)


class EmbedForms(Embed):

    @classmethod
    def coupang_main(cls: Type[E]) -> E:
        self: E = cls.__new__(cls)

        descriptions = {
            "골드박스": "https://coupa.ng/bSQUxy",
            "로켓프레쉬": "https://coupa.ng/bSQUDh",
            "로켓와우": "https://coupa.ng/bSQUFP",
            "로켓직구": "https://coupa.ng/bSQUJ4",
            "로켓배송": "https://coupa.ng/bSQUMW"
        }

        self.__init__(
            title="쿠팡",
            description="\n".join(f"▶ [**{k}**](<{v}>)" for k, v in descriptions.items()),
            url="https://coupa.ng/bSQJi8",
        )
        self.set_thumbnail(url="https://cdn.discordapp.com/attachments/804815694717911080/817096183637344286/img.png")

        return self

    @classmethod
    def search_output_simple(
        cls,
        name: str,
        url: str,
        price: Union[int, str],
        image_url: str,
        is_rocket: bool,
        rating: float,
        rating_count,
        discount_rate,
        base_price
    ):

        self = cls()

        def make_rating_to_moon():
            full_moon = int(rating)
            half_moon = rating % 1

            full_moons = "🌕" * full_moon

            if half_moon == 0.5:
                return f"{full_moons}🌗"

            return full_moons

        rating_info = ""

        if rating != "":
            rating_moon = make_rating_to_moon()
            rating_info = f" {rating_moon} ({rating_count:,})"

        price_text = f"**{price} 원**"

        if discount_rate == "":
            self.description = price_text

        else:
            self.description = f"{price_text}\n{discount_rate} ~~{base_price} 원~~"

        self.title = name
        self.url = url

        if is_rocket is True:
            author = f"🚀 {rating_info}"
            self.set_author(name=author)

        self.set_thumbnail(url=image_url)

        return self
