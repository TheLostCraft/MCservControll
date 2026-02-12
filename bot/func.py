import shelve

class GuildsData:
    def write(ctx, typ, content):
        if(typ == "name"):
            with shelve.open('Guilds_Data') as db:
                db[ctx.guild.id, "name"] = {content}


    def read(ctx, typ):
        if(typ == "name"):
            with shelve.open('Guilds_Data') as db:
                content = db.get(ctx.guild.id, "name")
        return content
