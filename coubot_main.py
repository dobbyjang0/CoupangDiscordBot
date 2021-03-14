import nest_asyncio
import asyncio
import discord
import pandas
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv

nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")
load_dotenv("token.env")

@bot.event
async def on_ready():
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user}")
    print(f"ID: {bot.user.id}")

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

<<<<<<< HEAD
@coupang.command(name="지원금")
async def Gcoupang_fund(ctx):
    #do stuff
    pass

# 킬 관련 커맨드
=======
>>>>>>> 36ed2eb1d918ab2919c69b595f11baff94b50bde
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
