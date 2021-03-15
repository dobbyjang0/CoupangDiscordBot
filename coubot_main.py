import nest_asyncio
import asyncio
import discord
import pandas
import os
import bs4
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

from res.Class import parser

nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")
load_dotenv("token.env")

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
    descriptions = {
        "골드박스": "https://coupa.ng/bSQUxy",
        "로켓프레쉬": "https://coupa.ng/bSQUDh",
        "로켓와우": "https://coupa.ng/bSQUFP",
        "로켓직구": "https://coupa.ng/bSQUJ4",
        "로켓배송": "https://coupa.ng/bSQUMW"
    }
    embed = discord.Embed(title="쿠팡", description="\n".join("▶ [**%s**](<%s>)" % (k, v) for k, v in descriptions.items()), url="https://coupa.ng/bSQJi8")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/804815694717911080/817096183637344286/img.png")
    await ctx.send(embed=embed)

@coupang.command(name="검색")
async def Gcoupang_search(ctx, count=3):
    embed = discord.Embed(title="상품의 이름 또는 링크를 입력해주세요.")
    msg = await ctx.send(embed=embed)

    async with ctx.typing():
        embed.set_footer(text="듣고 있어요. 편하게 말씀해주세요!")
        await msg.edit(embed=embed)
        wait_m = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    content = wait_m.content
    if content.startswith("https://"):
        if content.startswith("https://www.coupang.com/vp/products/"):
            pass
        else:
            embed.title = "이런!"
            embed.description = "올바른 쿠팡 상품 링크가 아닌 것 같아요."
            embed.color = discord.Colour.red()
            await msg.edit(embed=embed)
    else:
        embed.set_footer(text=discord.Embed.Empty)
        embed.title = "검색중이에요."
        await msg.edit(embed=embed)
        url = "https://www.coupang.com/np/search?component=&q=%s" % content
        items = parser.parser(url)
        await msg.delete()

        item_list = items.get_items(count)
        for item in item_list:
            embed = discord.Embed(title=item["name"], url=item['title_url'])
            author = ("🚀" if item["is_rocket"] else "") + item['rating'] + item['rating_count']
            embed.set_author(name = author)
            embed.add_field(name = item['price'], value=item['base_price']+item['discount_rate'])
            embed.set_thumbnail(url=item["image_url"])
            await ctx.send(embed=embed)

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
    embed = discord.Embed(title="봇이 %d 초 후 종료됩니다." % timer)
    msg = await ctx.send(embed=embed)

    async def countdown():
        global timer
        await msg.add_reaction("❌")

        while timer:
            timer -= 1
            await asyncio.sleep(1.0)
            embed.title = "봇이 %d 초 후 종료됩니다." % timer
            await msg.edit(embed=embed)
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
        embed.title = "종료를 취소합니다."
        await msg.edit(embed=embed, delete_after=5)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
