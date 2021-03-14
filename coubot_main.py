import nest_asyncio
import asyncio
import discord
from discord.ext import commands, tasks
import pandas

nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    return

@bot.command()
async def 쿠팡(ctx, service_type=None):
    if service_type in [None, "메인", "기본", "홈"]:
        embed = discord.Embed(title= "쿠팡", url="https://coupa.ng/bSQJi8")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/804815694717911080/817096183637344286/img.png")
        
        description_list=[]
        description_list.append("쿠팡 기본 홈페이지입니다.")
        description_list.append("▶ [**골드박스**](https://coupa.ng/bSQUxy)")
        description_list.append("▶ [**로켓프레쉬**](https://coupa.ng/bSQUDh)")
        description_list.append("▶ [**로켓와우**](https://coupa.ng/bSQUFP)")
        description_list.append("▶ [**로켓직구**](https://coupa.ng/bSQUJ4)")
        description_list.append("▶ [**로켓배송**](https://coupa.ng/bSQUMW)")
        embed.description='\n'.join(description_list)
        
        await ctx.send(embed=embed)
        return
    elif service_type == "지원금":
        # 지원금이 없는 경우 초기 지원금을 준다
        # 24시간이 지나면 지원금을 준다
        return

@bot.command()
async def 킬(ctx):
    if ctx.author.id not in [378887088524886016, 430377165629161482]:
        await ctx.send("권한없음")
        return
    await ctx.send("봇 꺼짐")
    await bot.close()    

def main():
    if __name__ == "__main__":
        #봇 실행
        with open("bot_token.txt", mode='r', encoding='utf-8') as txt:
            bot_token = txt.read()
        bot.run(bot_token)
        

        
main()