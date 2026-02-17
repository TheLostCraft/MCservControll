import discord
from discord.ext import commands

from func import Data
from func import processing
from func import Pterodactyl, Multicraft, AMP

from cryptography.fernet import Fernet
import os
import asyncio
import json

with open("encrypt_key.txt", "r") as file: # load the encrypton ojekt
      MASTER_KEY = file.read().strip()
fernet = Fernet(MASTER_KEY.encode())

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

        elif(SoftwareTyp.lower() == "multicraft"):
            await ctx.send("What is your API url")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            API_URL = msg.content

            await ctx.send("What is the Server ID")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            Server_ID = msg.content

            await ctx.send("What is the API Key")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            API_key = msg.content

            API_Login = [API_URL, Server_ID, API_key]

        elif(SoftwareTyp.lower() == "amp"):
            await ctx.send("What is your API url")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            API_URL = msg.content

            await ctx.send("What is the Server ID")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            Server_ID = msg.content

            await ctx.send("What is the API Key")
            msg = await bot.wait_for("message", timeout=1800, check=check)
            API_key = msg.content

            API_Login = [API_URL, Server_ID, API_key]

        else:
            await ctx.send("Your softwart does not exist in our database.\nProcess aborted")
            return


        # Last Question
        await ctx.send("Do you want to save the setup or cancel | Save, Cancel")
        msg = await bot.wait_for("message", timeout=1800, check=check)
        if(msg.content.lower() == "save"):
            # save data
            await Data.write(ctx, "SoftwareTyp", SoftwareTyp.lower())
            await Data.write(ctx, "API_Login", API_Login)

            await ctx.send(f"Your setup is saved \nSoftwareTyp: {SoftwareTyp}")

    except asyncio.TimeoutError:
        await ctx.send("Process aborted: Timeout")
        return


@bot.command()
async def rolePermission(ctx, Role: discord.Role, PermissionLevel: int):
    Permissions = await Data.read(ctx, "Permissions") or {}

    Permissions[str(Role.id)] = PermissionLevel
    await Data.write(ctx, "Permissions", Permissions)

    await ctx.send(f"Role '{Role.name}' has now a permission level of {PermissionLevel}")


@bot.command()
async def roleCommandPermission(ctx, Command: str, PermissionLevel: int):
    PermissionLevels = await Data.read(ctx, "PermissionLevels") or [0,0,0]

    if(Command.lower() == "start"):
        PermissionLevels[0] = PermissionLevel
        await Data.write(ctx, "PermissionLevels", PermissionLevels)
    elif(Command.lower() == "stop"):
        PermissionLevels[1] = PermissionLevel
        await Data.write(ctx, "PermissionLevels", PermissionLevels)
    elif(Command.lower() == "restart"):
        PermissionLevels[2] = PermissionLevel
        await Data.write(ctx, "PermissionLevels", PermissionLevels)
    else:
        return 
    
    await ctx.send(f"The command {prefix}{Command} needs now a permission level of {PermissionLevel}")

    



# start / stop / restart
@bot.command()
async def start(ctx):
    await processing.start(ctx, prefix)

@bot.command()
async def stop(ctx):
    await processing.stop(ctx, prefix)

@bot.command()
async def restart(ctx):
    await processing.restart(ctx, prefix)
    

# read the token of your discord bot and use it
with open("token.txt", "r") as file: # token.txt content = discord bot token
    token = file.read().strip()
bot.run(token)
