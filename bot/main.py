import discord
from discord.ext import commands
import shelve

prefix = '>' # <- Your prefix you want for your discord bot

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.command()
async def start(ctx):
    print("Start")


# read the token of your discord bot and use it
with open("token.txt", "r") as file: # token.txt content = discord bot token
    token = int(file.read())
bot.run(token)
