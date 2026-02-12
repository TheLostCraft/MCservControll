import discord
from discord.ext import commands
import shelve

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.command()
async def start(ctx):
    print("Start")



with shelve.open('Discord.Bot_Token') as db:
    token = db.get("token")
bot.run(token)