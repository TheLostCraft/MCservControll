import shelve

class Data: # save and read data

    # TYPs :
    # 1. SoftwareTyp          | Pterodactyl
    # 2. PermissionLevels     | Wo can do what. [start, stop, restart]
    # 3. PermissionRoleLevels |
    # 4. PermissionRoleIDs    |

    def write(ctx, typ, content): # save data
        with shelve.open('Guilds_Data') as db:
            db[ctx.guild.id, typ] = {content}


    def read(ctx, typ): # read data 
        with shelve.open('Guilds_Data') as db:
            content = db.get(ctx.guild.id, typ)
        
        return content
    

class processing:
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

    def start(ctx):
        if(Data.read(ctx, "PermissionLevels")[0] <= processing.getRolePermissonsLevel(ctx)):
            if(Data.read(ctx, "SoftwareTyp") == "Pterodactyl"):
                Pterodactyl.start


class Pterodactyl:
    def start(ctx):
        print()

