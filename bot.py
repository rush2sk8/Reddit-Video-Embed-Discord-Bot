import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from shutil import which

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
from pystreamable import StreamableApi

load_dotenv(dotenv_path=Path('.')/'.env')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
S_USER = os.getenv('S_USER')
S_PASS = os.getenv('S_PASS')


bot = commands.Bot(command_prefix='!', intents= discord.Intents.default())
streamable_api = StreamableApi(S_USER, S_PASS)

@bot.event
async def on_ready():
    """Event when the bot logs in"""
    await bot.change_presence(activity=discord.Streaming(name="by rush2sk8", url='https://www.twitch.tv/rush2sk8'))
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

    m = message.content

    if (re.search("http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", m)):
        if ("reddit" in m):
            url = f'{m[:-1]}.json'

            try:
                json = requests.get(url, headers = {'User-agent': 'reddit-discordbot'}).json()
                video_url = json[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]

                video_title = json[0]["data"]["children"][0]["data"]["title"]

                l = video_url.split("DASH")[0]
                r = video_url.split("?")[-1]

                audio_url = f'{l}DASH_audio.mp4?{r}'

                final_video_name = "video.mp4"

                urllib.request.urlretrieve(video_url, filename=final_video_name)

                try:
                    urllib.request.urlretrieve(audio_url, filename="audio.mp4")

                    subprocess.call (
                        "ffmpeg -y -hide_banner -loglevel error -i video.mp4 -i audio.mp4 -c:v copy -c:a aac output.mp4",
                        shell=True
                    )

                    final_video_name = "output.mp4"
                    os.remove("audio.mp4")

                except Exception:
                    pass

                shortcode = streamable_api.upload_video(final_video_name, video_title)['shortcode']

                while streamable_api.get_info(shortcode)["percent"] != 100:
                    time.sleep(1)

                await message.channel.send(f'https://streamable.com/{shortcode}')

                os.remove(final_video_name)
                os.remove("video.mp4")
            except Exception:
                pass

if which("ffmpeg") is not None:
    bot.run(DISCORD_TOKEN)
else:
    sys.exit("Bro install ffmpeg")
