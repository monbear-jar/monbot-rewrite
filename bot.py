import discord
from discord.ext import commands

import os, json, asyncio

botInfo = ".\\bot_info.json"

try:
    with open(botInfo, "r") as f:
        data=json.loads(f.read())
        cogs_blacklist = data["cogs_blacklist"]
        token = data["token"]
        prefix = data["prefix"]
        guildID = data["guildID"]
except FileNotFoundError:
    with open(botInfo, "w") as f:
        token = input("Bot Token: ")
        prefix = input("Command Prefix: ")
        guildID = input("Guild ID (Optional): ")
        botInfoData = {
            "token": token,
            "prefix": prefix,
            "guildID": guildID
        }
        json.dump(botInfoData, f, indent=2)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(prefix, intents=intents)


async def load_extensions():
    for cog in os.listdir('cogs'):
        if cog.endswith('.py'):
            if cog[:-3] in cogs_blacklist:
                pass
            else:
                await client.load_extension(f'cogs.{cog[:-3]}')

@client.event
async def on_ready():
    if guildID is not None:
        synced = await client.tree.sync(guild=discord.Object(id=guildID))
    else:
        synced = await client.tree.sync()
    print(synced)
    print(f'Logged into {client.user} \n Bot online!')

async def main():
    async with client:
        discord.utils.setup_logging()
        await load_extensions()
        await client.start(token)

asyncio.run(main())