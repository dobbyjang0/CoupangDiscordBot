import sys
import discord

from .errors import NoneFormname

def embed_factory(form_name, *arg, **kwargs):
    try:
        return getattr(sys.modules[__name__], form_name)(*arg, **kwargs)
    except AttributeError:
        raise NoneFormname(form_name)

#아래의 form들은 모두 이 클래스를 상속할 것
class formbase:
    def __init__(self, *arg, **kwarg):
        self.embed = discord.Embed()
        self.init_make()
        if arg is not None and kwarg is not None:
            self.insert(*arg, **kwarg)

    def init_make(self):
        pass

    def insert(self, *arg, **kwarg):
        pass

    @property
    def get(self):
        return self.embed

# 처음에 안바뀌는건 init_make, 처음에 값을 넣어줘야 되는건 insert에서 해줘야함
class coupang_main(formbase):
    def init_make(self):
        descriptions = {
        "골드박스": "https://coupa.ng/bSQUxy",
        "로켓프레쉬": "https://coupa.ng/bSQUDh",
        "로켓와우": "https://coupa.ng/bSQUFP",
        "로켓직구": "https://coupa.ng/bSQUJ4",
        "로켓배송": "https://coupa.ng/bSQUMW"
        }
        self.embed.title = "쿠팡"
        self.embed.description = "\n".join("▶ [**%s**](<%s>)" % (k, v) for k, v in descriptions.items())
        self.embed.url = "https://coupa.ng/bSQJi8"
        self.embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/804815694717911080/817096183637344286/img.png")

class serch_output_simple(formbase):
    def insert(self, name, url, price, image_url, is_rocket, rating,
               rating_count, discount_rate, base_price, **kwarg):
        def make_rating_to_moon(rating):
            full_moon = int(rating)
            half_moon = rating % 1
            return "🌕" * full_moon + ("🌗" if half_moon == 0.5 else "")
        
        if rating == "":
            rating_info = ""
        else:
            rating_moon = make_rating_to_moon(float(rating))
            rating_info = f" {rating_moon} {rating_count}"
            
        if discount_rate == "":
            discount_info = "."
        else:
            discount_info = f"{discount_rate} ~~{base_price}원~~"
        
        self.embed.title = name
        self.embed.url = url
        author = ("🚀" if is_rocket else "") + rating_info
        self.embed.set_author(name = author)
        self.embed.add_field(name="%s원" % price, value=discount_info)
        self.embed.set_thumbnail(url=image_url)
    

class serch_waiting(formbase):
    def init_make(self):
        self.embed.title = "상품의 이름 또는 링크를 입력해주세요."

    def insert(self, *arg, **kwarg):
        self.embed.set_footer(text="듣고 있어요. 편하게 말씀해주세요!")

class serch_ing(formbase):
    def init_make(self):
        self.embed.title = "검색중이에요."
        
class serch_oops(formbase):
    def init_make(self):
        self.embed.title = "이런!"
        self.embed.description = "올바른 쿠팡 상품 링크가 아닌 것 같아요."
        self.embed.color = discord.Colour.red()
        
class kill_count(formbase):
    def insert(self, timer, *arg, **kwarg):
        self.embed.title = "봇이 %d 초 후 종료됩니다." % timer
        
class kill_canceled(formbase):
    def init_make(self):
        self.embed.title = "종료를 취소합니다."
        
if __name__ == "__main__":
    print(embed_factory("kill_count", 5).embed.title)
