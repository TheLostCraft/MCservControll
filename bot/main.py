import discord
from discord import app_commands
from discord.ext import commands

from func import Data
from func import processing, FakeCTX
from func import Pterodactyl, Multicraft, AMP, CraftyController, PufferPanel

from cryptography.fernet import Fernet
import os
import aiohttp
import asyncio
import json
from datetime import datetime
import pytz
import threading

with open("encrypt_key.txt", "r") as file: # load the encrypton ojekt
      MASTER_KEY = file.read().strip()
fernet = Fernet(MASTER_KEY.encode())

PermissionLevelsFallSave = [0,0,0,0,0,0]

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">", intents=discord.Intents.default())

bot = MyBot()

@bot.event 
async def on_ready():
    await bot.tree.sync()

@bot.tree.command(name="setup", description="setup the discord bot")
@app_commands.choices(software=[
    app_commands.Choice(name="Pterodactyl", value="pterodactyl"),
    app_commands.Choice(name="Multicraft", value="multicraft"),
    app_commands.Choice(name="AMP", value="amp"),
    app_commands.Choice(name="CraftyController", value="craftycontroller"),
    app_commands.Choice(name="PufferPanel", value="pufferpanel"),
])
async def setup(
    interaction: discord.Interaction,
    software: app_commands.Choice[str],
    api_panel_url: str,
    server_id: str,
    api_key: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message( "Only administrators can use this command.", ephemeral=True)
        return

    API_Login = [api_panel_url, server_id, api_key]
    ctx = FakeCTX(interaction)

    await Data.write(ctx, "SoftwareTyp", software.value)
    await Data.write(ctx, "API_Login", API_Login)
    await interaction.response.send_message("Your data has been saved", ephemeral=True)
    await processing.Log(ctx, "/setup")


@bot.tree.command(name="rolepermission", description="set the role permission level")
@app_commands.describe(role="The role", permissionlevel="The permission level")
async def rolepermission(interaction: discord.Interaction, role: discord.Role, permissionlevel: int):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[4] <= await processing.getRolePermissonsLevel(ctx):

        Permissions = await Data.read(ctx, "Permissions") or {}

        Permissions[str(role.id)] = permissionlevel
        await Data.write(ctx, "Permissions", Permissions)

        await interaction.response.send_message(f"Role '{role.name}' has now a permission level of {permissionlevel}", ephemeral=True)
        await processing.Log(ctx, f"/rolepermission: {role.name} == {permissionlevel}")

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)

@bot.tree.command(name="rolecommandpermission", description="set the role permission level needed to do a command")
@app_commands.choices(command=[
    app_commands.Choice(name="Start", value="start"),
    app_commands.Choice(name="Stop", value="stop"),
    app_commands.Choice(name="Restart", value="restart"),
    app_commands.Choice(name="Status", value="status"),
    app_commands.Choice(name="RolePermission", value="rolepermission"),
    app_commands.Choice(name="RoleCommandPermission", value="rolecommandpermission"),
])
async def rolecommandpermission(
    interaction: discord.Interaction,
    command: app_commands.Choice[str],
    permissionlevel: int
):
    ctx = FakeCTX(interaction)
    PermissionLevels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if PermissionLevels[5] <= await processing.getRolePermissonsLevel(ctx):
        
        if(command.value == "start"):
            PermissionLevels[0] = permissionlevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "stop"):
            PermissionLevels[1] = permissionlevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "restart"):
            PermissionLevels[2] = permissionlevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "status"):
            PermissionLevels[4] = permissionlevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels) 
        elif(command.value == "rolepermission"):
            PermissionLevels[4] = permissionlevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "rolecommandpermission"):
            PermissionLevels[5] = permissionlevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        else:
           return 
    
        await interaction.response.send_message(f"The command /{command.value} needs now at least a permission level of {permissionlevel}", ephemeral=True)
        await processing.Log(ctx, f"/rolecommandpermission: /{command.value} <= {permissionlevel}")
    
    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)

    



# start / stop / restart
@bot.tree.command(name="status", description="status of your server")
async def status(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[3] <= await processing.getRolePermissonsLevel(ctx):

        await processing.status(ctx)
        await processing.Log(ctx, "/status")

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)


@bot.tree.command(name="start", description="start your server")
async def start(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[0] <= await processing.getRolePermissonsLevel(ctx):

        await processing.start(ctx)
        await processing.Log(ctx, "/start")

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)


@bot.tree.command(name="stop", description="stop your server")
async def stop(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[1] <= await processing.getRolePermissonsLevel(ctx):

        await processing.stop(ctx)
        await processing.Log(ctx, "/stop")

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)


@bot.tree.command(name="restart", description="Restart your server")
async def restart(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[2] <= await processing.getRolePermissonsLevel(ctx):
        
        await processing.restart(ctx)
        await processing.Log(ctx, "/restart")

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)

# stop it via terminal
def console_listener():
    while True:
        cmd = input()
        if cmd.lower() == "stop":
            print("The discord bot is shutting down...")
            # Beende den Bot sauber
            threading.Thread(target=lambda: bot.loop.create_task(bot.close())).start()
            break
listener_thread = threading.Thread(target=console_listener, daemon=True)
listener_thread.start()

# read the token of your discord bot and use it
with open("token.txt", "r") as file: # token.txt content = discord bot token
    token = file.read().strip()
bot.run(token)
