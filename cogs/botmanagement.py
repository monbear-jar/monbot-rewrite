import discord
from discord.ext import commands
from discord import app_commands

import os, sys
import subprocess
import json

botInfo = ".//bot_info.json"
with open(botInfo, 'r') as f:
    data = json.loads(f.read())
    ownerID = data["ownerID"]

class BotManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_me():
        def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == int(ownerID)
        return app_commands.check(predicate)

    def update_bot(self):
        commands = "git pull".split()
        print(commands)
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        output, error = process.communicate()

        print("Output:", output.decode())
        print("Error:", error.decode())

    def restart_bot(self):
        os.execv(sys.executable, ['python'] + sys.argv)

    @discord.app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @is_me()
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message('Restarting bot...')
        self.restart_bot()

    @discord.app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @is_me()
    async def update(self, interaction: discord.Interaction):
        await interaction.response.send_message('Updating bot...')
        self.update_bot()
        self.restart_bot()

async def setup(bot):
    await bot.add_cog(BotManagement(bot))

async def teardown(bot):
    await bot.remove_cog('BotManagement')