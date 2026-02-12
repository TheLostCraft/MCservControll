import discord
from discord.ext import commands

from func import 
import

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.command()
async def start(ctx):
    print("Start")


# read token and run with it

bot.run(token)

