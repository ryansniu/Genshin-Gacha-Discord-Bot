import os
import random
import gacha
import user

import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

standardBanner = gacha.StandardBanner()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='register', help='Registers the player into the database')
async def register(ctx):
    await ctx.send("Registered!" if user.create_new_user(ctx.guild, ctx.author) else "Already Registered!")

@bot.command(name='reset', help='Resets player data')
async def reset(ctx):
    player = user.get_player(ctx.guild, ctx.author)
    if player is not None:
        player.reset()
        player.write_to_db()
        await ctx.send("Reset Data!")
    else:
        await ctx.send("Player is not registered!")

@bot.command(name='delete', help='Deletes player data')
async def reset(ctx):
    await ctx.send("User deleted!" if user.delete_user(ctx.guild, ctx.author) else "User does not exists!")
    
@bot.command(name='one_pull', help='Simulates pulling on the banner once')
async def one_pull(ctx, banner : float):
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    if player is not None:
        wish = standardBanner.one_pull(player, banner)
        player.write_to_db()
        await ctx.send(wish)
    else:
        await ctx.send("Player is not registered!")

@bot.command(name='ten_pull', help='Simulates pulling on the banner ten times')
async def ten_pull(ctx, banner : float):
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    if player is not None:
        wishes = [standardBanner.one_pull(player, banner) for _ in range(10)]
        player.write_to_db()
        for wish in wishes:
            await ctx.send(wish)
            await asyncio.sleep(0.8)
    else:
        await ctx.send("Player is not registered!")

@bot.command(name='debug_pull', help='Simulates pulling on the banner 10X times')
async def debug_pull(ctx, banner : float, num : int):
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    if player is not None:
        for _ in range(10 * num):
            standardBanner.one_pull(player, banner)
        player.write_to_db()
        await ctx.send(player.get_debug_info())
    else:
        await ctx.send("Player is not registered!")

bot.run(TOKEN)
