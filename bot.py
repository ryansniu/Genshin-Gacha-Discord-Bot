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

testBanner = gacha.Banner()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='register', help='Registers the player into the database')
async def register(ctx):
    await ctx.send("Registered!" if user.create_new_user(ctx.guild, ctx.author) else "Already Registered!")
    
@bot.command(name='one_pull', help='Simulates pulling on the banner once')
async def one_pull(ctx, banner):
    #get member + server acc combo
    #if no data, say you got to register
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    if player is not None:
        wish = testBanner.one_pull(player, testBanner)
        player.write_to_db()
        await ctx.send(wish)
    else:
        await ctx.send("Player is not registered!")

@bot.command(name='ten_pull', help='Simulates pulling on the banner ten times')
async def ten_pull(ctx, banner):
    #get member + server acc combo
    #if no data, say you got to register
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    if player is not None:
        wishes = [testBanner.one_pull(player, testBanner) for _ in range(10)]
        player.write_to_db()
        for wish in wishes:
            await ctx.send(wish)
            await asyncio.sleep(0.8)
    else:
        await ctx.send("Player is not registered!")

@bot.command(name='reset', help='Resets player data')
async def reset(ctx):
    user.get_player(ctx.guild, ctx.author).reset()
    await ctx.send("Reset Data!")


bot.run(TOKEN)
