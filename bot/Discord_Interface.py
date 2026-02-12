import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.command()
async def start(ctx):
    print("Start")


# read token and run with it
with shelve.open('Discord.Bot_token') as db:
    token = db.get("token")
bot.run(token)
