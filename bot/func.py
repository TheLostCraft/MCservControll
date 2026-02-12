import shelve

class GuildsData:
    def write(ctx, typ, content):
        if(typ == "name"):
            with shelve.open('Guilds_Data') as db:
                db[ctx.guild.id, "name"] = {content}
        
        print()


    def read(ctx, typ):
        if(typ == "name"):
            with shelve.open('Guilds_Data') as db:
                ergebnis = db.get(ctx.guild.id, "name")