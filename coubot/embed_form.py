import sys
import discord

from typing import Union

from .errors import NoneFormName


def embed_factory(form_name, *arg, **kwargs):

    if hasattr(sys.modules[__name__], form_name):
        return getattr(sys.modules[__name__], form_name)(*arg, **kwargs)

    raise NoneFormName(form_name)


# 아래의 Form들은 모두 이 클래스를 상속할 것
class FormBase(discord.Embed):

    def get(self):
        return self

    @classmethod
    def coupang_main(cls):
        self = cls()

        descriptions = {
            "골드박스": "https://coupa.ng/bSQUxy",
            "로켓프레쉬": "https://coupa.ng/bSQUDh",
            "로켓와우": "https://coupa.ng/bSQUFP",
            "로켓직구": "https://coupa.ng/bSQUJ4",
            "로켓배송": "https://coupa.ng/bSQUMW"
        }

        self.title = "쿠팡"
        self.description = "\n".join("▶ [**%s**](<%s>)" % (k, v) for k, v in descriptions.items())
        self.url = "https://coupa.ng/bSQJi8"
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

            empty_moons = "🌕" * full_moon

            if half_moon == 0.5:
                return f"{empty_moons}🌗"

            return empty_moons

        if rating == "":
            rating_info = ""

        else:
            rating_moon = make_rating_to_moon()
            rating_info = f" {rating_moon} {rating_count}"

        price_text = f"**{price}원**"

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


class serch_waiting(FormBase):
    def init_make(self):
        self.embed.title = "상품의 이름 또는 링크를 입력해주세요."

    def insert(self, *arg, **kwarg):
        self.embed.set_footer(text="듣고 있어요. 편하게 말씀해주세요!")

class serch_ing(FormBase):
    def init_make(self):
        self.embed.title = "검색중이에요."
        
class serch_oops(FormBase):
    def init_make(self):
        self.embed.title = "이런!"
        self.embed.description = "올바른 쿠팡 상품 링크가 아닌 것 같아요."
        self.embed.color = discord.Colour.red()
        
class kill_count(FormBase):
    def insert(self, timer, *arg, **kwarg):
        self.embed.title = "봇이 %d 초 후 종료됩니다." % timer
        
class kill_canceled(FormBase):
    def init_make(self):
        self.embed.title = "종료를 취소합니다."
       
class extension_NotFound(FormBase):
    def init_make(self):
        self.embed.description = "확장자를 찾을 수 없습니다."

class extension_NotLoaded(FormBase):
    def init_make(self):
        self.embed.description = "로드되지 않은 확장자입니다."

if __name__ == "__main__":
    print(embed_factory("kill_count", 5).embed.title)
