import discord
from discord.ext import commands

import os, json, asyncio

botInfo = ".\\bot_info.json"
expectedKeys = ["token", "prefix", "ownerID", "guildID","cogs_blacklist"]

try:
    with open(botInfo, "r") as f:
        data = json.loads(f.read())
        token = data["token"]
        prefix = data["prefix"]
        ownerID = data["ownerID"]
        guildID = data["guildID"]
        cogsBlacklist = data["cogs_blacklist"]

except KeyError:
    with open(botInfo, "r+") as f:
        data = json.loads(f.read())
        newData = {}
        for key in expectedKeys:
            if data.get(key) is None:
                if key == "guildID":
                    data[key] = ''
                elif key == "cogs_blacklist":
                    data[key] = []
                else:
                    data[key] = input(f"Missing {key}, please type it now: ")
            else:
                pass
        
        data.update(newData)
        f.seek(0)
        json.dump(data, f, indent=2)

        token = data["token"]
        prefix = data["prefix"]
        ownerID = data["ownerID"]
        guildID = data["guildID"]
        cogsBlacklist = data["cogs_blacklist"]

except FileNotFoundError:
    with open(botInfo, "w+") as f:
        token = input("Bot Token: ")
        prefix = input("Command Prefix: ")
        ownerID = input("Your discord ID (for owner commands): ")
        guildID = input("Guild ID (Optional): ")
        cogsBlacklist = []
        botInfoData = {
            "token": token,
            "prefix": prefix,
            "guildID": guildID,
            "ownerID": ownerID,
            "cogs_blacklist": cogsBlacklist
        }
        json.dump(botInfoData, f, indent=2)
        
        f.seek(0)
        data = json.loads(f.read())
        token = data["token"]
        prefix = data["prefix"]
        ownerID = data["ownerID"]
        guildID = data["guildID"]
        cogsBlacklist = data["cogs_blacklist"]

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(prefix, intents=intents)


async def load_extensions():
    for cog in os.listdir('cogs'):
        if cog.endswith('.py'):
            if cog[:-3] in cogsBlacklist:
                pass
            else:
                await client.load_extension(f'cogs.{cog[:-3]}')

@client.event
async def on_ready():
    if guildID != "":
        synced = await client.tree.sync(guild=discord.Object(id=int(guildID)))
    else:
        synced = await client.tree.sync()
    print(synced)
    print(f'Logged into {client.user}\nBot online!')

async def main():
    async with client:
        discord.utils.setup_logging()
        await load_extensions()
        await client.start(token)

asyncio.run(main())