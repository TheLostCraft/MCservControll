import discord
from discord import app_commands
from discord.ext import commands

import aiohttp
import asyncio
from cryptography.fernet import Fernet
import json
import discord
from datetime import datetime
import pytz

with open("encrypt_key.txt", "r") as file:
      MASTER_KEY = file.read().strip()
fernet = Fernet(MASTER_KEY.encode())

class Data: # save and read data

    # TYPs :
    # SoftwareTyp          | pterodactyl, multicraft, amp
    # API_Login            | Pterodactly = [Panel_URL, Server_ID, API_key]; multicraft, AMP = [API_URL, Server_ID, API_key]
    # PermissionLevels     | Wo can do what. [start, stop, restart, status, RolePermission, RoleCommandPermission]
    # PermissionRoleLevels |
    # PermissionRoleIDs    |

    "bot-data-x284m"

    @staticmethod
    async def _get_channel(ctx, name):
        # look that the channel exsits
        for channel in ctx.guild.text_channels:
            if channel.name == name:
               return channel
            
        category_name = "MCservControll-Systhem"
        category = discord.utils.get(ctx.guild.categories, name=category_name)

        # Permission Overwrites
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
                read_messages=False,
                send_messages=False,
                manage_messages=False
            ),
            ctx.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True
            )
        }

        for role in ctx.guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_messages=True
                )

        # Create category
        if category is None:
            category = await ctx.guild.create_category(
                category_name,
                overwrites=overwrites,
                reason="Category for MCservControll channels"
            )
        
        # Create text-channel
        return await ctx.guild.create_text_channel(
            name,
            overwrites=overwrites,
            category=category,
            reason="MCserControll needs a private data storage channel"
        )

    @staticmethod
    async def _get_message(channel):
        async for msg in channel.history(limit=10):
            if msg.author == channel.guild.me:
                return msg
        return None


    @staticmethod
    async def read(ctx, key):
        channel = await Data._get_channel(ctx, "bot-data-x284m")
        msg = await Data._get_message(channel)

        if not msg:
            return None

        try:
            decrypted = Data.decrypt(msg.content)
            data = json.loads(decrypted)
        except Exception:
            data = {}
        return data.get(key)

    @staticmethod
    async def write(ctx, key, value):
        channel = await Data._get_channel(ctx, "bot-data-x284m")
        msg = await Data._get_message(channel)

        if msg:
            try:
                decrypted = Data.decrypt(msg.content)
                data = json.loads(decrypted)
            except Exception:
                data = {}
        else:
            data = {}

        data[key] = value

        content = Data.encrypt(json.dumps(data))

        if msg:
            await msg.edit(content=content)
        else:
            await channel.send(content)
    
    @staticmethod
    def encrypt(value):
        return fernet.encrypt(value.encode()).decode()
    
    @staticmethod
    def decrypt(value):
        return fernet.decrypt(value.encode()).decode()
    

class FakeCTX:
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.author = interaction.user
        self.bot = interaction.client
        self._deferred = False

    async def send(self, content: str, ephemeral: bool = True):
        if not self._deferred:
            try:
                await self.interaction.response.defer(ephemeral=ephemeral)
                self._deferred = True
            except Exception:
                pass

        await self.interaction.followup.send(content, ephemeral=ephemeral)

    

class processing:
    @staticmethod
    async def Log(ctx,action):
        utc_zone = pytz.timezone("Etc/UTC")  # neutral, always 0 UTC
        now = datetime.now(utc_zone)

        channel = await Data._get_channel(ctx, "logs")

        await channel.send(f"{now.strftime('%d.%m.%Y | %H:%M:%S')} : {ctx.author.name}: {action}")

    @staticmethod
    async def getRolePermissonsLevel(ctx):
        Permissions = await Data.read(ctx, "Permissions") or {}
        user_roles = [str(role.id) for role in ctx.author.roles]
 
        levels = [Permissions[role_id] for role_id in user_roles if role_id in Permissions]

        if levels:
            return max(levels)
        return 0 

    @staticmethod
    async def getServerSoftware(ctx):
        Software = await Data.read(ctx, "SoftwareTyp")

        if(Software == "pterodactyl"):
            return Pterodactyl()
        elif(Software == "multicraft"):
            return Multicraft()
        elif(Software == "amp"):
            return AMP()
        elif(Software == "craftycontroller"):
            return CraftyController()
        elif(Software == "pufferpanel"):
            return PufferPanel()
        else:
            return None
 
 
    @staticmethod
    async def status(ctx):
        server = await processing.getServerSoftware(ctx) # software class ( AMP() )
        if not server:
            await ctx.send(f"Server not configured. Use /setup first.")
            return
        server_status = (await server.status(ctx)).lower()

        await ctx.send(f"The server status is {server_status}")

    @staticmethod
    async def start(ctx):
        server = await processing.getServerSoftware(ctx) # software class ( AMP() )
        if not server:
            await ctx.send(f"Server not configured. Use /setup first.")
            return
        server_status = (await server.status(ctx)).lower()

            
        if(server_status != "running" and server_status != "starting" and server_status != "restarting" and server_status != "stopping"):
            await ctx.send(f"The server is starting now. Current state: {server_status}")
            await server.power_action(ctx, "start")

        elif(server_status == "running" or server_status == "starting" or server_status == "restarting"):
            await ctx.send(f"The server is already {server_status}")

        elif(server_status == "stopping"):
            await ctx.send("The server is stoppint, let it to that befor you start it")

        else:
            await ctx.send(f"Hopefully you never see this message: Error: Status: {server_status}")        
            

    @staticmethod
    async def stop(ctx):   
        server = await processing.getServerSoftware(ctx) # software class ( AMP() )
        if not server:
            await ctx.send(f"Server not configured. Use /setup first.")
            return
        server_status = (await server.status(ctx)).lower()
        if(server_status == "running"):
            await server.power_action(ctx, "stop")
            await ctx.send(f"The server is stoping now.")

        elif(server_status == "stopping" or server_status == "offline" or server_status == "stopped" or server_status == "crashed"):
            await ctx.send(f"The server is already {server_status}")

        elif(server_status == "starting" or server_status == "restarting"):
            await ctx.send(f"The server is {server_status}, let it to that befor you start it")

        elif(server_status == "unknown" or server_status == "failed"):
            await ctx.send(f"The server state is {server_status} but I try to stop it")
            await server.power_action(ctx, "stop")

        else:
            await ctx.send(f"Hopefully you never see this message: Error: Status: {server_status}")


    @staticmethod
    async def restart(ctx):        
        server = await processing.getServerSoftware(ctx) # software class ( AMP() )
        if not server:
            await ctx.send(f"Server not configured. Use /setup first.")
            return
        server_status = (await server.status(ctx)).lower()
                    
        if(server_status == "running"):
            await server.power_action(ctx, "restart")
            await ctx.send(f"The server is stoping now.")
        elif(server_status == "restarting"):
            await ctx.send(f"The server is already {server_status}")
        elif(server_status == "starting"):
            await ctx.send(f"The server is {server_status}, let it to that befor you start it")

        elif(server_status == "offline" or server_status == "stopping" or server_status == "crashed"):#
            await ctx.send(f"You can't restat the server, the status {server_status}")

        elif(server_status == "unknown" or server_status == "failed"):
            await ctx.send(f"The server state is {server_status} but I try to stop it")
            await server.power_action(ctx, "stop")

        else:
            await ctx.send(f"Hopefully you never see this message: Error: Status: {server_status}")
                

class ServerInterface:
    @staticmethod
    async def status(ctx):
        raise NotImplementedError

    @staticmethod
    async def power_action(ctx, action):
        raise NotImplementedError
    

class Pterodactyl(ServerInterface):
    @staticmethod
    async def status(ctx):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        Panel_URL, Server_ID, API_key = API_Login

        headers = {
            "Authorization": f"Bearer {API_key}",
            "Accept": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{Panel_URL}/api/client/servers/{Server_ID}/resources", headers=headers) as resp:
                if resp.status != 200:
                    return "error"
                data = await resp.json()
                return data["attributes"]["current_state"]

    @staticmethod
    async def power_action(ctx, action):  # "start", "stop", "restart"
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        Panel_URL, Server_ID, API_key = API_Login

        headers = {
            "Authorization": f"Bearer {API_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{Panel_URL}/api/client/servers/{Server_ID}/power",
                                    headers=headers, json={"signal": action}) as resp:
                return await resp.text()


class Multicraft(ServerInterface):
    @staticmethod
    async def status(ctx):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, data={
                'action': 'status',
                'server': Server_ID,
                'apikey': API_key
            }) as resp:
                if resp.status != 200:
                    return "unknown"
                result = await resp.json()
                return result.get('status', 'unknown')

    @staticmethod
    async def power_action(ctx, action):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, data={
                'action': action,
                'server': Server_ID,
                'apikey': API_key
            }) as resp:
                return await resp.text()


class AMP(ServerInterface):
    @staticmethod
    async def status(ctx):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        headers = {"Authorization": f"Bearer {API_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/servers/{Server_ID}", headers=headers) as resp:
                if resp.status != 200:
                    return "Unknown"
                data = await resp.json()
                return data.get("State", "Unknown").lower()

    @staticmethod
    async def power_action(ctx, action):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        headers = {"Authorization": f"Bearer {API_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_URL}/servers/{Server_ID}/{action}", headers=headers) as resp:
                return await resp.text()


class CraftyController:
    @staticmethod
    async def power_action(ctx, action):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {API_key}"}
        ) as session:
            async with session.post(
                f"{API_URL}/servers/{Server_ID}/action/{action}"
            ) as resp:
                return resp.status == 200 
    
    @staticmethod
    async def status(ctx):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {API_key}"}
        ) as session:
            async with session.get(
                f"{API_URL}/servers/{Server_ID}/stats"
            ) as resp:
                data = await resp.json()
                status = data.get("running", False)
                if(status == True):
                    return "running"
                elif(status == False):
                    return "offline"
                else:
                    return "unknown"
                

class PufferPanel:
    @staticmethod
    async def power_action(ctx, action):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        HEADERS = {
        "Authorization": f"Bearer {API_key}",
        "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.post(
                f"{API_URL}/servers/{Server_ID}/{action}"
            ) as resp:
                return resp.status == 204
            
    @staticmethod
    async def status(ctx):
        API_Login = await Data.read(ctx, "API_Login")
        if not API_Login:
            return "not_configured"
        API_URL, Server_ID, API_key = API_Login

        HEADERS = {
        "Authorization": f"Bearer {API_key}",
        "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(f"{API_URL}/servers/{Server_ID}") as resp:
               data = await resp.json()
               return data["status"]
