import shelve

token = input("What is the token of your discord bot? ")
token = int(token)

with shelve.open('Discord.Bot_Token') as db:
                db['token'] = {token}

print(f"Your discord bot token is {token}")