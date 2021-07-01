from discord.ext import commands

from ..Class import db
from ..Class import parser


class AlarmCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_alarm(self, ctx, product_id, product_price=None):
        if product_id is None:
            await ctx.send(f'입력 오류')
            return
        
        # 현재 가격 스캔, 나중에 파셔쪽에서 클래스 분리, 함수화 시키기
        url = f"https://www.coupang.com/vp/products/{product_id}"
        print(url)
        cou_parser = parser.parser(url)

        if not cou_parser.get_item_detail():
            await ctx.send('없는 제품')
            return

        print(cou_parser.get_item_detail())
        
        now_price = cou_parser.get_item_detail()['price']
          
        if not product_price:
            product_price = now_price
        
        # 알람 목록에 추가시킨다.
        alarm_table = db.PriceAlarmTable()
        await alarm_table.insert(ctx.guild.id, ctx.channel.id, ctx.author.id, product_id, product_price)
        
        await ctx.send((product_id, product_price, ctx.author.id, "저장완료"))
        
        # 스캔 목록에 추가시킨다.
        scan_table = db.ScanTable()
        if scan_table.read_by_id(product_id) is None:
            await scan_table.insert(product_id, now_price)

        print("스캔목록 저장완료")
        return

    async def read_alarm_list(self, ctx):
        alarm_table = db.PriceAlarmTable()
        alarm_list = alarm_table.read_by_user(ctx.author.id)
        await ctx.send(alarm_list)
        return

    async def delete_alarm(self, ctx, product_id):
        if not product_id:
            await ctx.send(f'값 미입력')
            return
        
        if not product_id.isdigit():
            await ctx.send('숫자 입력 바람')
            return
        
        product_id = int(product_id)
        
        alarm_table = db.PriceAlarmTable()
        await alarm_table.delete_by_id(ctx.author.id, product_id)
        await ctx.send(f'{product_id}삭제 완료')
        return
    
    async def update_alarm(self, ctx, product_id, product_price):
        if not product_id or not product_price:
            await ctx.send(f'입력 오류')
            return
        
        if not product_id.isdigit() and not product_price.isdigit():
            await ctx.send('숫자 입력 바람')
            return
        
        product_id = int(product_id)
        product_price = int(product_price)
        
        alarm_table = db.PriceAlarmTable()
        await alarm_table.update_price(ctx.channel.id, ctx.channel.id, ctx.author.id, product_id)

        await ctx.send(f'{product_id} {product_price}로 수정 완료')
        return
            
    
def setup(bot):
    bot.add_cog(AlarmCog(bot))
