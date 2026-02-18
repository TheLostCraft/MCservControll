import discord
from discord import app_commands
from discord.ext import commands

from func import Data
from func import processing, FakeCTX
from func import Pterodactyl, Multicraft, AMP

from cryptography.fernet import Fernet
import os
import asyncio
import json

with open("encrypt_key.txt", "r") as file: # load the encrypton ojekt
      MASTER_KEY = file.read().strip()
fernet = Fernet(MASTER_KEY.encode())

PermissionLevelsFallSave = [0,0,0,0,0]

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">", intents=discord.Intents.default())

bot = MyBot()

@bot.event 
async def on_ready():
    await bot.tree.sync()

@bot.tree.command(name="setup", description="setup the discord bot")
@app_commands.describe(software_typ="What software do you use", panel_url="Your panel/api url", server_id="Your sever id", api_key="Your API key")
async def setup(interaction: discord.Interaction, software_typ: str, panel_url: str, server_id: str, api_key: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message( "Only administrators can use this command.", ephemeral=True)
        return

    API_Login = [panel_url, server_id, api_key]
    ctx = FakeCTX(interaction)

    await Data.write(ctx, "SoftwareTyp", software_typ.lower())
    await Data.write(ctx, "API_Login", API_Login)
    await interaction.response.send_message("Your data has been saved", ephemeral=True)


@bot.tree.command(name="rolepermission", description="set the role permission level")
@app_commands.describe(role="The role", permissionlevel="The permission level")
async def RolePermission(interaction: discord.Interaction, role: discord.Role, permissionlevel: int):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[3] <= await processing.getRolePermissonsLevel(ctx):

        Permissions = await Data.read(ctx, "Permissions") or {}

        Permissions[str(role.id)] = permissionlevel
        await Data.write(ctx, "Permissions", Permissions)

        await interaction.response.send_message(f"Role '{role.name}' has now a permission level of {permissionlevel}", ephemeral=True)

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)

@bot.tree.command(name="rolecommandpermission", description="set the role permission level needed to do a command")
@app_commands.choices(command=[
    app_commands.Choice(name="Start", value="start"),
    app_commands.Choice(name="Stop", value="stop"),
    app_commands.Choice(name="Restart", value="restart"),
    app_commands.Choice(name="RolePermission", value="rolepermission"),
    app_commands.Choice(name="RoleCommandPermission", value="rolecommandpermission"),
])
async def RoleCommandPermission(
    interaction: discord.Interaction,
    command: app_commands.Choice[str],
    PermissionLevel: int
):
    ctx = FakeCTX(interaction)
    PermissionLevels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if PermissionLevels[4] <= await processing.getRolePermissonsLevel(ctx):
        
        if(command.value == "start"):
            PermissionLevels[0] = PermissionLevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "stop"):
            PermissionLevels[1] = PermissionLevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "restart"):
            PermissionLevels[2] = PermissionLevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "rolepermission"):
            PermissionLevels[3] = PermissionLevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        elif(command.value == "rolecommandpermission"):
            PermissionLevels[4] = PermissionLevel
            await Data.write(ctx, "PermissionLevels", PermissionLevels)
        else:
           return 
    
        await interaction.response.send_message(f"The command /{command} needs now a permission level of {PermissionLevel}", ephemeral=True)
    
    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)

    



# start / stop / restart
@bot.tree.command(name="start", description="start your server")
async def start(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[0] <= await processing.getRolePermissonsLevel(ctx):

        await processing.start(ctx)

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)


@bot.tree.command(name="stop", description="stop your server")
async def stop(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[1] <= await processing.getRolePermissonsLevel(ctx):

        await processing.stop(ctx)

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)


@bot.tree.command(name="restart", description="Restart your server")
async def restart(interaction: discord.Interaction):
    ctx = FakeCTX(interaction)

    permission_levels = await Data.read(ctx, "PermissionLevels") or PermissionLevelsFallSave
    if permission_levels[2] <= await processing.getRolePermissonsLevel(ctx):
        
        await processing.restart(ctx)

    else:
        await interaction.response.send_message("You do not the permission to do that", ephemeral=True)
    

# read the token of your discord bot and use it
with open("token.txt", "r") as file: # token.txt content = discord bot token
    token = file.read().strip()
bot.run(token)
