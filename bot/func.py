import shelve
import aiohttp


class Data: # save and read data

    # TYPs :
    # SoftwareTyp          | pterodactyl, multicraft, amp
    # API_Login            | Pterodactly = [Panel_URL, Server_ID, API_key]; multicraft, AMP = [API_URL, Server_ID, API_key]
    # PermissionLevels     | Wo can do what. [start, stop, restart]
    # PermissionRoleLevels |
    # PermissionRoleIDs    |

    @staticmethod
    def write(ctx, typ, content): # save data
        with shelve.open('Guilds_Data') as db:
            db[f"{ctx.guild.id}_{typ}"] = content


    @staticmethod
    def read(ctx, typ): # read data 
        with shelve.open('Guilds_Data') as db:
            content = db.get(f"{ctx.guild.id}_{typ}")
        
        return content
    

class processing:
    @staticmethod
    def getRolePermissonsLevel(ctx):
        Permissions = Data.read(ctx, "Permissions") or {}
        user_roles = [str(role.id) for role in ctx.author.roles]
 
        levels = [Permissions[role_id] for role_id in user_roles if role_id in Permissions]

        if levels:
            return max(levels)
        return 0 
   

    def getServerSoftware(ctx):
        Software = Data.read(ctx, "SoftwareTyp")

        if(Software == "pterodactyl"):
            return Pterodactyl()
        elif(Software == "multicraft"):
            return Multicraft()
        elif(Software == "amp"):
            return AMP()


    @staticmethod
    async def start(ctx):
        if(Data.read(ctx, "PermissionLevels")[0] <= processing.getRolePermissonsLevel(ctx)):
            server = processing.getServerSoftware(ctx) # software class ( AMP() )
            server_status = server.status(ctx).lower()
            
            if(server_status != "running" or server_status != "starting" or server_status != "restarting" or server_status != "stopping"):
                await ctx.send(f"The server is starting now. Current state: {server_status}")
                server.power_action(ctx, "start")

            elif(server_status == "running" or server_status == "starting" or server_status == "restarting"):
                await ctx.send(f"The server is already {server_status}")

            elif(server_status == "stopping"):
                await ctx.send("The server is stoppint, let it to that befor you start it")

            else:
                await ctx.send(f"Hopefully you never see this message: Error: Status: {server_status}")
  
        else:
            await ctx.send("You don't have the permission to do this")           
            

    @staticmethod
    async def stop(ctx):
        if(Data.read(ctx, "PermissionLevels")[1] <= processing.getRolePermissonsLevel(ctx)):
            
            server = processing.getServerSoftware(ctx) # software class ( AMP() )
            server_status = server.status(ctx).lower()
            
            if(server_status == "running"):
                server.power_action(ctx, "stop")
                await ctx.send(f"The server is stoping now.")

            elif(server_status == "stopping" or server_status == "offline" or server_status == "stopped" or server_status == "crashed"):
                await ctx.send(f"The server is already {server_status}")

            elif(server_status == "starting" or server_status == "restarting"):
                await ctx.send(f"The server is {server_status}, let it to that befor you start it")

            elif(server_status == "unknown" or server_status == "failed"):
                await ctx.send(f"The server state is {server_status} but I try to stop it")
                server.power_action(ctx, "stop")

            else:
                await ctx.send(f"Hopefully you never see this message: Error: Status: {server_status}")
  
        else:
            await ctx.send("You don't have the permission to do this")  


    @staticmethod
    async def restart(ctx):
        if(Data.read(ctx, "PermissionLevels")[2] <= processing.getRolePermissonsLevel(ctx)):
            
            server = processing.getServerSoftware(ctx) # software class ( AMP() )
            server_status = server.status(ctx).lower()
            
            if(server_status == "running"):
                server.power_action(ctx, "restart")
                await ctx.send(f"The server is stoping now.")

            elif(server_status == "restarting" or server_status):
                await ctx.send(f"The server is already {server_status}")

            elif(server_status == "starting"):
                await ctx.send(f"The server is {server_status}, let it to that befor you start it")

            elif(server_status == "offline" or server_status == "stopping" or server_status == "crashed"):#
                await ctx.send(f"You can't restat the server, the status {server_status}")

            elif(server_status == "unknown" or server_status == "failed"):
                await ctx.send(f"The server state is {server_status} but I try to stop it")
                server.power_action(ctx, "stop")

            else:
                await ctx.send(f"Hopefully you never see this message: Error: Status: {server_status}")
  
        else:
            await ctx.send("You don't have the permission to do this")
                

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
        API_Login = Data.read(ctx, "API_Login")
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
        API_Login = Data.read(ctx, "API_Login")
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
        API_Login = Data.read(ctx, "API_Login")
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
        API_Login = Data.read(ctx, "API_Login")
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
        API_Login = Data.read(ctx, "API_Login")
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
        API_Login = Data.read(ctx, "API_Login")
        API_URL, Server_ID, API_key = API_Login

        headers = {"Authorization": f"Bearer {API_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_URL}/servers/{Server_ID}/{action}", headers=headers) as resp:
                return await resp.text()
