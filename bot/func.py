import shelve
import requests


class Data: # save and read data

    # TYPs :
    # SoftwareTyp          | pterodactyl
    # API_Login            | Pterodactly = [Panel_URL, Server_ID, API_key]
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
        Role_Levels = Data.read(ctx, "PermissionRoleLevels")
        Role_IDs = Data.read(ctx, "PermissionRoleIDs")
        
        if(len(Role_IDs) == len(Role_Levels)):
            
            if any(role.id in Role_IDs for role in ctx.author.roles):
                equal_IDs = [i for i, value in enumerate(Role_IDs) if value in [role.id for role in ctx.author.roles]]
                PermissionLevel = 0
                
                while len(equal_IDs) != 0:
                    if(PermissionLevel < Role_Levels[equal_IDs[0]]):
                        PermissionLevel = Role_Levels[equal_IDs[0]]
                        equal_IDs.pop(0)
                    else:
                        equal_IDs.pop(0)
            
            else:
                PermissionLevel = 0
                    
        else:
            print(f"Error the number of Role_IDs is not th same as Role_Levels \nRole_IDs : {Role_IDs} \nRole_Levels : {Role_Levels}")

        return PermissionLevel


   
    @staticmethod
    async def start(ctx):
        if(Data.read(ctx, "PermissionLevels")[0] <= processing.getRolePermissonsLevel(ctx)):
            if(Data.read(ctx, "SoftwareTyp") == "pterodactyl"):
                
                if(Pterodactyl.status(ctx) == "offline"):
                    Pterodactyl.power_action(ctx, "start")
                    await ctx.send("The server starts")
                
                elif(Pterodactyl.status(ctx) == "running" or Pterodactyl.status(ctx) == "starting"):
                    await ctx.send(f"The is server already {Pterodactyl.status(ctx)}")
                
                elif(Pterodactyl.status(ctx) == "stopping"):
                    await ctx.send("Let it stop before you start it")

                else:
                    (f"Something went wrong. Have you already set up the system? \nError: {Pterodactyl.status(ctx)}")


    @staticmethod
    async def stop(ctx):
        if(Data.read(ctx, "PermissionLevels")[1] <= processing.getRolePermissonsLevel(ctx)):
            if(Data.read(ctx, "SoftwareTyp") == "pterodactyl"):
                
                if(Pterodactyl.status(ctx) == "running"):
                    Pterodactyl.power_action(ctx, "stop")
                    await ctx.send("The server stops")
                
                elif(Pterodactyl.status(ctx) == "offline" or Pterodactyl.status(ctx) == "stopping"):
                    await ctx.send(f"The is server already {Pterodactyl.status(ctx)}")
                
                elif(Pterodactyl.status(ctx) == "starting"):
                    await ctx.send("Let it start before you stop it")

                else:
                    (f"Something went wrong. Have you already set up the system? \nError: {Pterodactyl.status(ctx)}")


    @staticmethod
    async def restart(ctx):
        if(Data.read(ctx, "PermissionLevels")[1] <= processing.getRolePermissonsLevel(ctx)):
            if(Data.read(ctx, "SoftwareTyp") == "pterodactyl"):
                
                if(Pterodactyl.status(ctx) == "running"):
                    Pterodactyl.power_action(ctx, "restart")
                    await ctx.send("The server restarts")
                
                elif(Pterodactyl.status(ctx) == "offline"):
                    await ctx.send(f"The is server already {Pterodactyl.status(ctx)}")
                
                elif(Pterodactyl.status(ctx) == "starting" or Pterodactyl.status(ctx) == "stopping"):
                    await ctx.send(f"It is {Pterodactyl.status(ctx)}, let it do that  before you restart it")

                else:
                    (f"Something went wrong. Have you already set up the system? \nError: {Pterodactyl.status(ctx)}")
                


class Pterodactyl:
    @staticmethod
    def power_action(ctx, action): # action = "start", "stop", "restart"
        API_Login = Data.read(ctx, "API_Login")
        Panel_URL = API_Login[0]
        Server_ID = API_Login[1]
        API_key = API_Login[2]

        HEADERS = {
            "Authorization": f"Bearer {API_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        requests.post(
            f"{Panel_URL}/api/client/servers/{Server_ID}/power",
            headers=HEADERS,
           json={"signal": action}
        )

    
    @staticmethod
    def status(ctx): # return = "offline", "running", "starting", "stopping"

        API_Login = Data.read(ctx, "API_Login")
        Panel_URL = API_Login[0]
        Server_ID = API_Login[1]
        API_key = API_Login[2]

        HEADERS = {
            "Authorization": f"Bearer {API_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        Server_Ressources = requests.get(
            f"{Panel_URL}/api/client/servers/{Server_ID}/resources",
            headers=HEADERS
        ).json()
        return Server_Ressources["attributes"]["current_state"]
