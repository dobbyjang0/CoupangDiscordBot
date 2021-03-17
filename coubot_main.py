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
from res.Class.embed_form import embed_factory as embed_maker

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
    await ctx.send(embed=embed_maker("coupang_main").get)

@coupang.command(name="검색")
async def Gcoupang_search(ctx, count=3):
    embed_waiting = embed_maker("serch_waiting")
    msg = await ctx.send(embed=embed_waiting.get)

    async with ctx.typing():
        embed_waiting.insert("go")
        await msg.edit(embed=embed_waiting.get)
        wait_m = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

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
        
        for item in item_list:
            await ctx.send(embed=embed_maker("serch_output_simple",**item).get)

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
    bot.run(os.getenv('DISCORD_TOKEN'))
