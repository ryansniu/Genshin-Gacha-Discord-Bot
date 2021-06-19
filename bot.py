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

current_genshin_version = 1.6

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
async def one_pull(ctx, banner_id, version = current_genshin_version):
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    banner =  gacha.get_banner(banner_id, version)
    if player is not None and banner is not None and banner.banner_type != gacha.BannerType.BEGINNER:
        wish = banner.one_pull(player)
        player.write_to_db()
        await ctx.send(wish)
    else:
        if player is None:
            await ctx.send("Player is not registered!")
        if banner is None:
            await ctx.send("Banner does not exist!")
        if banner.banner_type == gacha.BannerType.BEGINNER:
            await ctx.send("Cannot roll once on Beginner Banner!")

@bot.command(name='ten_pull', help='Simulates pulling on the banner ten times')
async def ten_pull(ctx, banner_id, version = current_genshin_version):
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    banner = gacha.get_banner(banner_id, version)
    if banner.banner_type == gacha.BannerType.BEGINNER and player.get_num_beginner_rolls() >= 2:
        await ctx.send("Cannot pull more than twice on Beginner Banner!")
    elif player is not None and banner is not None:
        wishes = [banner.one_pull(player) for _ in range(10)] if banner.banner_type != gacha.BannerType.BEGINNER else banner.ten_pull(player)
        player.write_to_db()
        for wish in wishes:
            await ctx.send(wish)
            await asyncio.sleep(0.8)
    else:
        if player is None:
            await ctx.send("Player is not registered!")
        if banner is None:
            await ctx.send("Banner does not exist!")
            

@bot.command(name='debug_pull', help='Simulates pulling on the banner 10X times')
async def debug_pull(ctx, banner_id, num : int, version = current_genshin_version):
    #if not enough primos, say you don't have enough primos
    player = user.get_player(ctx.guild, ctx.author)
    banner = gacha.get_banner(banner_id, version)
    if player is not None and banner is not None and banner.banner_type != gacha.BannerType.BEGINNER:
        for _ in range(10 * num):
            banner.one_pull(player)
        player.write_to_db()
        await ctx.send(player.get_debug_info())
    else:
        if player is None:
            await ctx.send("Player is not registered!")
        if banner is None:
            await ctx.send("Banner does not exist!")
        if banner.banner_type == gacha.BannerType.BEGINNER:
            await ctx.send("Cannot debug roll on Beginner Banner!")

@bot.command(name='get_inventory', help='Returns the player inventory')
async def get_inventory(ctx):
    player = user.get_player(ctx.guild, ctx.author)
    inventory = player.get_inventory()
    if len(inventory) == 0:
        await ctx.send("Paimon says you should spend money and roll!")
    else:
        await ctx.send(inventory)

@bot.command(name='get_history', help='Returns the player history')
async def get_history(ctx):
    player = user.get_player(ctx.guild, ctx.author)
    history = player.get_history()
    if len(history) == 0:
        await ctx.send("Paimon says you should spend money and roll!")
    else:
        await ctx.send(history)

bot.run(TOKEN)
