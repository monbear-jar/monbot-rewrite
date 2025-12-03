import discord
from discord.ext import commands
from discord import app_commands

import os
import random, yt_dlp, string, functools, validators, asyncio, aiohttp, requests
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

resourceDir = ".//cogs//resources//"
mediaDir = ".//cogs//resources//downloader//"
mp3Dir = ".//cogs//resources//downloader//mp3"
mp4Dir = ".//cogs//resources//downloader//mp4"

dirList = [resourceDir, mediaDir, mp3Dir, mp4Dir]

for folder in dirList:
    try:
        os.path.isdir(folder)
    except FileNotFoundError:
        os.mkdir(folder)

class Downloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def download_media(self, url, formattype):
        try:
            randomString = ''.join(random.choice(string.ascii_letters) for x in range(10))
            if formattype == 'mp3':
                ydl_opts = {
                    'outtmpl': f'{mp3Dir}//%(title)s ({randomString}).%(ext)s',
                    'format': 'mp3/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }]
                }
                saveDir = mp3Dir
            elif formattype == 'mp4':
                ydl_opts = {
                    'outtmpl': f'{mp4Dir}//%(title)s ({randomString}).%(ext)s',
                    'format': 'mp4'
                }
                saveDir = mp4Dir

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                infoDict = ydl.extract_info(url, download=False)
                rawTitle = infoDict.get('title', None)
                error_code = ydl.download(url)

            title = rawTitle.translate(str.maketrans('','', string.punctuation)) + f"_({randomString})"
            os.rename(f'{saveDir}//{rawTitle} ({randomString}).{formattype}', f'{saveDir}//{title}.{formattype}')
            size = os.path.getsize(f"{saveDir}//{title}.{formattype}")
            varlist = [title, rawTitle]
            if size > 10000000:
                with open(f'{saveDir}//{title}.{formattype}', 'rb') as file:
                    url = requests.post('https://uguu.se/upload.php', files={'file': file}).json()['files'][0]['url']
                    return {"title":title, "rawTitle":rawTitle,"url":url}
            elif size < 10000000:
                return {"title":title, "rawTitle":rawTitle}
        except yt_dlp.utils.DownloadError as e:
            return {"error":e}

    @discord.app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.choices(formatchoice=[
        app_commands.Choice(name='video', value="mp4"),
        app_commands.Choice(name='audio', value="mp3"),
    ])
    async def download(self, interaction: discord.Interaction, url: str, formatchoice: app_commands.Choice[str]) -> None:
        formattype = formatchoice.value
        if formattype == 'mp3':
            saveDir = mp3Dir
        elif formattype == 'mp4':
            saveDir = mp4Dir
        
        if validators.url(url) == True:
            message = await interaction.response.send_message(f"Downloading '{url}', please wait.", ephemeral=True)
            loop = asyncio.get_event_loop()
            downloadData = await loop.run_in_executor(ThreadPoolExecutor(), functools.partial(self.download_media, url, formattype))
            if downloadData.get('error') is None:
                if downloadData.get('url') is not None:
                    await interaction.followup.send(f"Downloaded [{downloadData["rawTitle"]}](<{url}>)\nLink: {downloadData["url"]}")
                else:
                    await interaction.followup.send(f"Downloaded [{downloadData["rawTitle"]}](<{url}>)", file = discord.File(f'{saveDir}//{downloadData["title"]}.{formattype}'))

                os.remove(f'{saveDir}//{downloadData["title"]}.{formattype}')
            else:
                await interaction.followup.send(f'Download failed\nError: ``{downloadData["error"]}``')
        else:
            await interaction.response.send_message(f"'{url}' is not a valid url.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Downloader(bot))

async def teardown(bot):
    await bot.remove_cog('Downloader')