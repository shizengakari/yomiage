import discord
import TOKEN
import traceback
import json
import os
from discord.ext import commands

bot = commands.Bot(command_prefix="",intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user.name} ({bot.user.id}) がログインしました。')

    for file in os.listdir("./cog"):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.{file[:-3]}')
                print(f"Loaded cogs: cog.{file[:-3]}")
            except Exception as e:
                print(f"cog.{file[:-3]} failed to load")
                traceback.print_exc()

    try:
        await bot.load_extension("jishaku")
        print("Loaded extension: Jishaku")
    except Exception:
        traceback.print_exc()
        
    try:
        synced = await bot.tree.sync()
        for guild in bot.guilds:
            await bot.tree.sync(guild=guild)
        print(f"INFO {len(synced)}のコマンドを同期をしました。")
    except Exception as error:
        print(f"ERROR コマンドの同期に失敗しました。\nエラー内容\n**{error}**")

    
#トークンをここで入力
