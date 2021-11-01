import os
import time
import coubot
import asyncio
import nest_asyncio

from tendo import singleton
from dotenv import load_dotenv
from discord.ext import commands
from coubot.coupang import CoupangClient
from discord_slash import SlashCommand, SlashContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import *

from coubot import triggers
from coubot.embed_form import embed_factory as embed_maker

nest_asyncio.apply()
me = singleton.SingleInstance()

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(
    bot,
    sync_commands=True,
    override_type=True
)
test_guild_ids = [820642064365649930]

coupang_client = CoupangClient(loop=bot.loop)

load_dotenv("token.env")

extensions = (
    'cogs.alarms',
    'cogs.admin_commands'
)


@bot.event
async def on_ready():
    coupang_client.login(
        access_key="dd9f93c9-4d02-4b6b-94e2-1e3c3aa04947",
        secret_key="6eed060216ccd101efea0b74d0e014e199b004d0"
    )

    sched = AsyncIOScheduler(timezone="Asia/Seoul")
    sched.add_job(triggers.AlarmTrigger(bot).test_process, 'interval', seconds=30)
    sched.start()

    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user}")
    print(f"ID: {bot.user.id}")


# 쿠팡 커맨드
@slash.subcommand(
    base="쿠팡",
    name="검색",
    description="쿠팡에서 검색을 합니다.",
    options=[
        create_option(
            name="검색어",
            description="검색어를 입력해주세요.",
            option_type=3,
            required=True
        ),
        create_option(
            name="드롭다운",
            description="드롭 다운 형식을 사용하시겠습니까?",
            option_type=5,
            required=False
        ),
        create_option(
            name="나만보기",
            description="우리 둘뿐이에요.",
            option_type=5,
            required=False
        ),
        create_option(
            name="개수",
            description="표시할 최대 개수를 입력해주세요.",
            option_type=4,
            required=False
        )
    ],
    connector={
        "검색어": "search_term",
        "개수": "count",
        "드롭다운": "dropdown",
        "나만보기": "hidden"
    },
    guild_ids=test_guild_ids
)
async def group_coupang_cmd_search(
        ctx: SlashContext,
        search_term: str,
        count: int = 3,
        dropdown: bool = False,
        hidden: bool = False
):

    if count > 9:
        embed = discord.Embed(description="최대 9개의 결과만 얻을 수 있습니다.")
        return await ctx.send(embed=embed, hidden=True)

    if coubot.utils.is_startswith_http_url(search_term):

        if not search_term.startswith("https://www.coupang.com/vp/products/"):
            embed = coubot.FormBase.invalid_coupang_url()
            return await ctx.send(embed=embed)

        embed = discord.Embed()
        embed.set_image(url="")
        return await ctx.send(embed=embed)

    products = await coupang_client.search_products(keyword=search_term, limit=count)

    if products is None:
        return await ctx.send("검색결과가 없습니다.")

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

    button_action_row = create_actionrow(*buttons)

    embeds = []

    for product in products:
        embed = coubot.FormBase.search_output_simple(
            name=product.name,
            url=product.url,
            price=product.price,
            image_url=product.image_url,
            is_rocket=product.is_rocket(),
            rating=1.0,
            rating_count=1.0,
            discount_rate=1.0,
            base_price=1
        )
        embeds.append(embed)

    if dropdown is False:

        for embed in embeds:
            await ctx.send(
                embed=embed,
                components=[button_action_row],
                hidden=hidden
            )

        select_ctx = await wait_for_component(
            client=bot,
            components=[button_action_row]
        )

    else:
        select_options = []

        for idx, embed in enumerate(embeds):
            option = create_select_option(
                label=coubot.utils.label_maker(embed.title),
                description=embed.description,
                value=str(idx),
                emoji=f"{idx + 1}\U000020E3"
            )
            select_options.append(option)

        def get_select(disable: bool = False, placeholder: str = "이곳에서 상품을 선택해주세요."):

            select = create_select(
                options=select_options,
                custom_id="select_product",
                placeholder=placeholder,
                min_values=1,
                max_values=1,
                disabled=disable
            )

            return create_actionrow(select)

        components = [get_select()]

        msg = await ctx.send(
            embeds=embeds,
            hidden=hidden,
            components=components
        )

        start_time = time.time()

        while time.time() - start_time <= 120:

            select_ctx = await wait_for_component(
                client=bot,
                messages=msg,
                components=components
            )

            first_selected_option = select_ctx.selected_options[0]
            selected_index: int = int(first_selected_option)

            embed = embeds[selected_index]

            components[0] = get_select(True, placeholder=embed.title)
            components.append(coubot.utils.pon_buttons())

            await select_ctx.edit_origin(
                content="이 상품으로 보시겠습니까?",
                embeds=[embed],
                components=components
            )

            button_ctx = await wait_for_component(
                client=bot,
                messages=msg,
                components=components
            )

            if button_ctx.custom_id == "true_btn":
                return

            components[0] = get_select()
            del components[1]

            await button_ctx.edit_origin(
                content=None,
                embed=embed,
                components=components
            )


async def registration(ctx, product_id=None, product_price=None):
    alarms = bot.get_cog('AlarmCog')
    print(product_id, product_price)
    await alarms.add_alarm(ctx, product_id, product_price)

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


@slash.subcommand(
    base="cogs",
    name="load",
    description="load cog",
    options=[
        create_option(
            name="cog_path",
            description="cog 파일의 경로",
            option_type=3,
            required=True
        )
    ],
    guild_ids=test_guild_ids
)
async def load(ctx, cog_path: str):

    try:
        bot.load_extension(cog_path)

    except commands.ExtensionNotFound:
        embed = embed_maker("extension_NotFound")
        await ctx.send(embed=embed)

    except commands.ExtensionAlreadyLoaded:
        embed = discord.Embed(description="이미 불러와져있습니다.")
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(description="로드 성공")
        await ctx.send(embed=embed)


@slash.subcommand(
    base="cogs",
    name="unload",
    description="unload cog",
    options=[
        create_option(
            name="cog_path",
            description="cog 파일의 경로",
            option_type=3,
            required=True
        )
    ],
    guild_ids=test_guild_ids
)
async def unload(ctx, cog_path):

    try:
        bot.unload_extension(cog_path)

    except commands.ExtensionNotFound:
        embed = embed_maker("extension_NotFound")
        await ctx.send(embed=embed)

    except commands.ExtensionNotLoaded:
        embed = embed_maker("extension_NotLoaded")
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(description="언로드 성공")
        await ctx.send(embed=embed)


@slash.subcommand(
    base="cogs",
    name="reload",
    description="reload cog",
    options=[
        create_option(
            name="cog_path",
            description="cog 파일의 경로",
            option_type=3,
            required=True
        )
    ],
    guild_ids=test_guild_ids
)
async def reload(ctx, name):
    try:
        bot.reload_extension(name)
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
