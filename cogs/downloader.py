import discord
from discord.ext import commands
from discord import app_commands

import os
import random, yt_dlp, string, functools, validators, asyncio, aiohttp, requests
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

mp3Dir = ".//cogs//resources//downloader//mp3"
mp4Dir = ".//cogs//resources//downloader//mp4"

if os.path.isdir(mp4Dir) == False:   
    os.mkdir(mp4Dir)
elif os.path.isdir(mp3Dir) == False:
    os.mkdir(mp3Dir)
else:
    pass

class Downloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def download_media(self, url, formattype):
        if formattype == 'audio':
            randomString = ''.join(random.choice(string.ascii_letters) for x in range(10))
            ydl_opts = {
                'outtmpl': f'{mp3Dir}//%(title)s ({randomString}).%(ext)s',
                'format': 'mp3/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                infoDict = ydl.extract_info(url, download=False)
                rawTitle = infoDict.get('title', None)
                error_code = ydl.download(url)
            title = rawTitle.translate(str.maketrans('','', string.punctuation)) + f"_({randomString})"
            os.rename(f'{mp3Dir}//{rawTitle} ({randomString}).mp3', f'{mp3Dir}//{title}.mp3')
            size = os.path.getsize(f".//cogs//resources//mp3//{title}.mp3")
            varlist = [title, rawTitle]
            if size > 10000000:
                with open(f'{mp3Dir}//{title}.mp3', 'rb') as mp3:
                    url = requests.post('https://uguu.se/upload.php', files={'files[]': mp3}).json()['files'][0]['url']
                    return {"title":title, "rawTitle":rawTitle,"url":url}
            elif size < 10000000:
                return {"title":title, "rawTitle":rawTitle}
        elif formattype == 'video':
            randomString = ''.join(random.choice(string.ascii_letters) for x in range(10))
            ydl_opts = {
                'outtmpl': f'{mp4Dir}//%(title)s ({randomString}).%(ext)s',
                'format': 'mp4'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                infoDict = ydl.extract_info(url, download=False)
                rawTitle = infoDict.get('title', None)
                error_code = ydl.download(url)
            title = rawTitle.translate(str.maketrans('','', string.punctuation)) + f"_({randomString})"
            os.rename(f'{mp4Dir}//{rawTitle} ({randomString}).mp4', f'{mp4Dir}//{title}.mp4')
            size = os.path.getsize(f".//cogs//resources//mp4//{title}.mp4")
            if size > 10000000:
                with open(f'{mp4Dir}//{title}.mp4', 'rb') as mp4:
                    url = requests.post('https://uguu.se/upload.php', files={'files[]': mp4}).json()['files'][0]['url']
                    return {"title":title, "rawTitle":rawTitle,"url":url}
            elif size < 10000000:
                return {"title":title, "rawTitle":rawTitle}
    
    @discord.app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def download(self, interaction: discord.Interaction, url: str, formattype: Literal['video','audio']):
        if validators.url(url) == True:
            message = await interaction.response.send_message(f"Downloading '{url}', please wait.", ephemeral=True)
            print(formattype)
            loop = asyncio.get_event_loop()
            downloadData = await loop.run_in_executor(ThreadPoolExecutor(), functools.partial(self.download_media, url, formattype))
            
            if downloadData.get('url') is not None:
                await interaction.followup.send(f"Downloaded [{downloadData["rawTitle"]}](<{downloadData["url"]}>) \n Link: {downloadData["url"]}")
            else:
                await interaction.followup.send(f"Downloaded [{downloadData["rawTitle"]}](<{url}>)", file = discord.File(f'{mp3Dir}//{downloadData["title"]}.mp3'))
                
            if formattype == 'audio':
                os.remove(f'{mp3Dir}//{downloadData["title"]}.mp3')
            elif formattype == 'video':
                os.remove(f'{mp4Dir}//{downloadData["title"]}.mp4')
        else:
            await interaction.response.send_message(f"'{url}' is not a valid url.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Downloader(bot))

async def teardown(bot):
    await bot.remove_cog('Downloader')