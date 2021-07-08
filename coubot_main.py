import os
import coubot
import asyncio
import discord
import nest_asyncio

from coupang import CoupangClient
from tendo import singleton
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash.model import ButtonStyle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord_slash.utils.manage_components import *


from coubot import triggers
from coubot.embed_form import embed_factory as embed_maker

nest_asyncio.apply()
me = singleton.SingleInstance()

bot = commands.Bot(command_prefix="!")
load_dotenv("token.env")

coupang_client = CoupangClient(loop=bot.loop)

extensions = [
    "res.Cogs.alarms"
]

@bot.event
async def on_ready():
    sched = AsyncIOScheduler(timezone="Asia/Seoul")
    sched.add_job(triggers.AlarmTrigger(bot).test_process, 'interval', seconds=30)
    sched.start()

    coupang_client.login(
        access_key="dd9f93c9-4d02-4b6b-94e2-1e3c3aa04947",
        secret_key="6eed060216ccd101efea0b74d0e014e199b004d0"
    )

    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user}")
    print(f"ID: {bot.user.id}")

#@bot.event
#async def on_command_error(error):
#    pass


@bot.command(name="test")
async def test_command(ctx, url):
    link = await coupang_client.get_link(url)
    await ctx.send(link)

# 쿠팡 관련 커맨드
@bot.group(name="쿠팡")
async def coupang(ctx):
    if ctx.subcommand_passed is None:
        embed = discord.Embed() # 나중에 설명 추가
        await ctx.send(embed=embed)


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
        cou_parser = coubot.Parser(url)
        await msg.delete()

        item_list = cou_parser.get_items(count)
        
        if item_list is None:
            return await ctx.send("검색결과가 없습니다.")

        for item in item_list:
            embed = coubot.FormBase.search_output_simple(**item)
            buttons = [
                create_button(
                    style=ButtonStyle.secondary,
                    emoji="🔍",
                    custom_id="search_btn"
                ),
                create_button(
                    style=ButtonStyle.secondary,
                    emoji="🔔",
                    custom_id="bell_btn"
                ),
                create_button(
                    style=ButtonStyle.secondary,
                    emoji="📥",
                    custom_id="save_to_wish_btn"
                )
            ]

            action_row = create_actionrow(*buttons)

            msg = await ctx.send(embed=embed, components=[action_row])
            button_ctx = await wait_for_component(client=bot, messages=msg)

            print(button_ctx.origin_message_id)


@bot.command(name="등록")
async def registration(ctx, product_id=None, product_price=None):
    alarms = bot.get_cog('AlarmCog')
    print(product_id, product_price)
    await alarms.add_alarm(ctx, product_id, product_price)

@bot.command(name="목록")
async def alarm_list(ctx):
    alarms = bot.get_cog('AlarmCog')
    await alarms.read_alarm_list(ctx)

@bot.command(name="삭제")
async def alarm_delete(ctx, product_id=None):
    alarms = bot.get_cog('AlarmCog')
    await alarms.delete_alarm(ctx, product_id)   

@bot.command(name="가격수정")
async def update_alarm(ctx, product_id=None, product_price=None):
    alarms = bot.get_cog('AlarmCog')
    await alarms.update_alarm(ctx, product_id, product_price)   

# --- Team Only Commands --- #

async def get_appinfo(): # 팀들을 User로 얻기
    return await bot.application_info()

def is_teamembers(): # 팀 멤버 확인 Decorator
    def predicate(ctx):
        app_info = asyncio.run(get_appinfo())
        team = app_info.team
        return ctx.author in team.members
    return commands.check(predicate)

@bot.group()
@is_teamembers()
async def cogs(ctx):
    pass

@cogs.command()
async def load(ctx, name, package=None):
    try:
        bot.load_extension(name, package)
    except commands.ExtensionNotFound:
        embed = embed_maker("extension_NotFound")
        await ctx.send(embed=embed)
    except commands.ExtensionAlreadyLoaded:
        embed = discord.Embed(description="이미 불러와져있습니다.")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description="로드 성공")
        await ctx.send(embed=embed)

@cogs.command()
async def unload(ctx, name, package=None):
    try:
        bot.unload_extension(name, package)
    except commands.ExtensionNotFound:
        embed = embed_maker("extension_NotFound")
        await ctx.send(embed=embed)
    except commands.ExtensionNotLoaded:
        embed = embed_maker("extension_NotLoaded")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description="언로드 성공")
        await ctx.send(embed=embed)

@cogs.command()
async def reload(ctx, name, package=None):
    try:
        bot.reload_extension(name, package)
    except commands.ExtensionNotFound:
        embed = embed_maker("extension_NotFound")
        await ctx.send(embed=embed)
    except commands.ExtensionNotLoaded:
        embed = embed_maker("extension_NotLoaded")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description="리로드 성공")
        await ctx.send(embed=embed)

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
        except Exception as error:
            print('fail to load %s: %s' % (extension, error))
        else:
            print('loaded %s' % extension)

    bot.run(os.getenv('DISCORD_TOKEN'))
