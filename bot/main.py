import discord
from discord.ext import commands

from func import Data
from func import processing
from func import Pterodactyl

import shelve
import asyncio


prefix = '>' # <- Your prefix you want for your Discord bot

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.command()
async def setup(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        # Question 1
        await ctx.send("What software do you use | Pterodactyl")
        msg = await bot.wait_for("message", timeout=1800, check=check)
        SoftwareTyp = msg.content


        if(SoftwareTyp.lower() == "pterodactyl"):
            await ctx.send("What is your Panel url")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            Panel_URL = msg.content

            await ctx.send("What is the Server ID")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            Server_ID = msg.content

            await ctx.send("What is the API Key")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            API_key = msg.content

            API_Login = [Panel_URL, Server_ID, API_key]

        else:
            await ctx.send("Your softwart does not exist in our database, I can only do Pterodactyl.\nProcess aborted")
            return


        # Last Question
        await ctx.send("Do you want to save the setup or cancel | Save, Cancel")
        msg = await bot.wait_for("message", timeout=1800, check=check)
        if(msg.content.lower() == "save"):
            # save data
            Data.write(ctx, "SoftwareTyp", SoftwareTyp.lower())
            Data.write(ctx, "API_Login", API_Login)

            await ctx.send(f"Your setup is saved \nSoftwareTyp: {SoftwareTyp}")

    except asyncio.TimeoutError:
        await ctx.send("Process aborted: Timeout")
        return


@bot.command()
async def start(ctx):
    await processing.start(ctx)

@bot.command()
async def start(ctx):
    await processing.stop(ctx)

@bot.command()
async def start(ctx):
    await processing.restart(ctx)
    

# read the token of your discord bot and use it
with open("token.txt", "r") as file: # token.txt content = discord bot token
    token = int(file.read())
bot.run(token)
