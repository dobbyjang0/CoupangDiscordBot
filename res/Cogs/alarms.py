import discord
from discord.ext import commands

from ..Class import parser
from ..Class import db

class alarms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="등록")
    async def add_alarm(self, ctx, product_id, product_price=None):
        # 현재 가격 스캔, 나중에 파셔쪽에서 클래스 분리, 함수화 시키기
        url = "https://www.coupang.com/vp/products/%s" % product_id
        cou_parser = parser.parser(url)
        if not cou_parser.get_item_detail():
            await ctx.send('없는 제품')
            return
        now_price = cou_parser.get_item_detail()['price']
          
        if not product_price:
            product_price = now_price
        
        #알람 목록에 추가시킨다.
        alarm_table = db.PriceAlarmTable()
        alarm_table.insert(ctx.guild.id, ctx.channel.id, ctx.author.id, product_id, product_price)
        
        await ctx.send((product_id, product_price, ctx.author.id, "저장완료"))
        
        #스캔 목록에 추가시킨다.
        scan_table = db.ScanTable()
        if scan_table.read_by_id(product_id) is None:
            scan_table.insert(product_id, now_price)

        print("스캔목록 저장완료")

def setup(bot):
    bot.add_cog(alarms(bot))
