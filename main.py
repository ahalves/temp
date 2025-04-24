import discord
from discord.ext import commands
import aiohttp
import asyncio
import os

TOKEN = "MTM2NDY2MzUzNjk2OTcxMTYxNg.Gi0ZJb.Mu9JgQv00zvbbQ6IvR2xetPfmWKBQD9NWuV7V8"  # Replace with your bot token
CHANNEL_ID = 1362711826760208394  # Replace with your Discord channel ID as an integer

WINDOWS_FILE = "windows.txt"
MAC_FILE = "mac.txt"
ANDROID_FILE = "android.txt"

intents = discord.Intents.all()

# Use commands.Bot instead of discord.Client for handling commands
client = commands.Bot(command_prefix="!", intents=intents)

# Helper functions to read and write version info to files
def read_version(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return f.read().strip()
    return None

def write_version(file, version):
    with open(file, "w") as f:
        f.write(version)

# Fetch versions of Windows, Mac, and Android
async def fetch_versions():
    headers = {
        "User-Agent": "WEAO-3PService"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://weao.xyz/api/versions/current") as win_mac_resp, \
                   session.get("https://weao.xyz/api/versions/android") as android_resp:

            win_mac_data = await win_mac_resp.json() if win_mac_resp.status == 200 else {}
            android_data = await android_resp.json() if android_resp.status == 200 else {}

            return {**win_mac_data, **android_data}

# Task to check for version updates every minute
async def version_task():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found.")
        return

    while not client.is_closed():
        data = await fetch_versions()
        if data:
            win_version = data.get("Windows")
            mac_version = data.get("Mac")
            android_version = data.get("Android")

            win_date = data.get("WindowsDate", "Unknown")
            mac_date = data.get("MacDate", "Unknown")
            android_date = data.get("AndroidDate", "Unknown")

            old_win = read_version(WINDOWS_FILE)
            old_mac = read_version(MAC_FILE)
            old_android = read_version(ANDROID_FILE)

            embed = discord.Embed(title="🔔 ROBLOX UPDATE", color=0x00FF50)
            updated = False

            if win_version and win_version != old_win:
                embed.add_field(
                    name="🪟 Windows Updated",
                    value=(f"**Old:** `{old_win or 'N/A'}`\n"
                           f"**New:** `{win_version}`\n"
                           f"📅 Date: `{win_date}`"),
                    inline=False
                )
                await channel.send("<@&1365001312483147928>")
                write_version(WINDOWS_FILE, win_version)
                updated = True

            if mac_version and mac_version != old_mac:
                embed.add_field(
                    name="🍎 Mac Updated",
                    value=(f"**Old:** `{old_mac or 'N/A'}`\n"
                           f"**New:** `{mac_version}`\n"
                           f"📅 Date: `{mac_date}`"),
                    inline=False
                )
                await channel.send("<@&1365000957200564234>")
                write_version(MAC_FILE, mac_version)
                updated = True

            if android_version and android_version != old_android:
                embed.add_field(
                    name="📱 Android Updated",
                    value=(f"**Old:** `{old_android or 'N/A'}`\n"
                           f"**New:** `{android_version}`\n"
                           f"📅 Date: `{android_date}`"),
                    inline=False
                )
                await channel.send("<@&1365001337258901564>")
                write_version(ANDROID_FILE, android_version)
                updated = True

            if updated:
                embed.add_field(name="\n\nEVERY IDE ON THE PLATFORM(S) MENTIONED IS DOWN UNTIL IT UPDATES!", value="")
                await channel.send(embed=embed)

        await asyncio.sleep(60)  # 1 minute interval

# Event when bot is ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    # Create the version check task after the bot is ready
    client.loop.create_task(version_task())

# Run the bot
client.run(TOKEN)
