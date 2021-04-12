import nest_asyncio
import asyncio
import discord
import pandas
import os
import bs4
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

from res.Class import db
from res.Class import parser
from res.Class.embed_form import embed_factory as embed_maker

nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")
load_dotenv("token.env")

extensions = [
    #cogs
]

@bot.event
async def on_ready():
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user}")
    print(f"ID: {bot.user.id}")

#@bot.event
#async def on_command_error(error):
#    pass

# 쿠팡 관련 커맨드
@bot.group(name="쿠팡")
async def coupang(ctx):
    pass

@coupang.command(name="메인", aliases=["기본", "홈"])
async def Gcoupang_main(ctx):
    await ctx.send(embed=embed_maker("coupang_main").get)

@coupang.command(name="검색")
async def Gcoupang_search(ctx, count=3):
    embed_waiting = embed_maker("serch_waiting")
    msg = await ctx.send(embed=embed_waiting.get)
    
    async with ctx.typing():
        embed_waiting.insert("go")
        await msg.edit(embed=embed_waiting.get)
        wait_m = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    try:
        await wait_m.delete()
    except discord.Forbidden:
        pass

    content = wait_m.content
    if content.startswith("https://"):
        if content.startswith("https://www.coupang.com/vp/products/"):
            pass
        else:
            await msg.edit(embed=embed_maker("serch_oops").get)
    else:
        await msg.edit(embed=embed_maker("serch_ing").get)
        
        url = "https://www.coupang.com/np/search?component=&q=%s" % content
        cou_parser = parser.parser(url)
        await msg.delete()
        item_list = cou_parser.get_items(count)
        
        if item_list is None:
            await ctx.send("검색결과가 없습니다.")
            return

        emojis = ["🔍", "🔔", "📥"]
        for item in item_list:
            msg = await ctx.send(embed=embed_maker("serch_output_simple",**item).get)
            for emoji in emojis:
                await msg.add_reaction(emoji)
        reaction, user = await bot.wait_for("reaction_add", check=lambda r, u: r.emoji in emojis and r.me is True)

# 킬 관련 커맨드
async def get_appinfo():
    return await bot.application_info()

def is_teamembers():
    def predicate(ctx):
        app_info = asyncio.run(get_appinfo())
        team = app_info.team
        return ctx.author in team.members
    return commands.check(predicate)

@bot.command(name="킬")
@is_teamembers()
async def kill_bot(ctx):
    global timer
    timer = 5
    embed_timer = embed_maker("kill_count", timer)
    msg = await ctx.send(embed=embed_timer.get)

    async def countdown():
        global timer
        await msg.add_reaction("❌")

        while timer:
            timer -= 1
            await asyncio.sleep(1.0)
            embed_timer.insert(timer)
            await msg.edit(embed=embed_timer.get)
        return False

    done, pending = await asyncio.wait([
        countdown(),
        bot.wait_for('reaction_add', check=lambda r, u: r.emoji == "❌" and u == ctx.author)
    ], return_when=asyncio.FIRST_COMPLETED)

    for future in pending:
        future.cancel()
                
    if not done.pop().result():
        await msg.delete()
        await bot.close()
    else:
        await msg.edit(embed=embed_maker("kill_canceled").get, delete_after=5)

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print('loaded %s' % extension)
        except Exception as error:
            print('fail to load %s: %s' % (extension, error))
        else:
            print('loaded %s' % extension)

    bot.run(os.getenv('DISCORD_TOKEN'))


###############################
## 임시 커맨드, cog로 바꿀 것 ##
###############################

# 알람 대상에 등록시킨다.
@bot.command(name="등록")
async def add_alarm(ctx, product_id, product_price=None):
    # 현재 가격 스캔, 나중에 파셔쪽에서 클래스 분리, 함수화 시키기
    url = "https://www.coupang.com/vp/products/%s" % product_id
    cou_parser = parser.parser(url)
    now_price = cou_parser.get_item_detail()['price']
      
    if not product_price:
        product_price = now_price
      
    #알람 목록에 추가시킨다.
    alarm_table = db.PriceAlarmTable()
    alarm_table.insert(ctx.guild.id, ctx.channel.id, ctx.author.id, product_id, product_price)
    
    await ctx.send((product_id, product_price, ctx.author.id, '저장완료'))
    
    #스캔 목록에 추가시킨다.
    scan_table = db.ScanTable()
    if scan_table.read_by_id(product_id) is None:
        scan_table.insert(product_id, now_price)

    print("스캔목록 저장완료")
    
# 하루마다 목록을 스캔한다. 알림을 보낸다.
@tasks.loop(hours=24)
async def alarm_process():
    scan_table = db.ScanTable()
    record_table = db.SaleRecordTable()
    alarm_table = db.PriceAlarmTable()
    
    # 스캔 대상 제품 스캔
    scan_df = scan_table.read_all()
    for idx in scan_df.index:
        product_id = scan_df.at[idx, 0]
        latest_price = scan_df.at[idx, 1]
        
        # 현재 가격 스캔, 나중에 파셔쪽에서 클래스 분리, 함수화 시키기
        url = "https://www.coupang.com/vp/products/%s" % product_id
        cou_parser = parser.parser(url)
        now_price = cou_parser.get_item_detail()['price']
        
        if now_price != latest_price:
            record_table.insert(product_id, now_price)
            scan_table.update(product_id, now_price)
    
    #알람 보낸다.
    alarm_df = alarm_table.read_today()
    for idx in alarm_df.index:
        channel_id = alarm_df[idx, 1]
        product_id = alarm_df[idx, 3]
        price = alarm_df[idx, 4]
        
        channel = bot.get_channel(channel_id)
        
        await channel.send(f"제품코드 {product_id} 가격 {price}로 변동됨")
    
    pass
