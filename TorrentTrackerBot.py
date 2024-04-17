import discord
from discord.ext import commands, tasks
import qbittorrentapi
import asyncio
import os

# Configuration Settings
config = {
    'qbt_host': 'localhost',            # Replace 'localhost' with the IP address of your qBittorrent server.
    'qbt_port': 8080,                   # Replace if Using Non-Default Web Port
    'qbt_username': 'admin',            # Replace 'admin' with your qBittorrent username.
    'qbt_password': 'yourpassword',     # Replace 'yourpassword' with your qBittorrent password.
    'discord_token': 'your_bot_token',  # Replace 'your_bot_token' with your Discord bot token.
    'discord_command_prefix': '$',      # Future Implementation
    'update_channel_id': 'Channel_ID',  # Set update_channel_id to the ID of the Discord channel where you want the updates to be sent.
}


# Initialize the qBittorrent client
qbt_client = qbittorrentapi.Client(
    host=config['qbt_host'],
    port=config['qbt_port'],
    username=config['qbt_username'],
    password=config['qbt_password']
)

# Initialize Discord Bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix=config['discord_command_prefix'], intents=intents, help_command=None)

# Async function to fetch torrent info using executor
async def fetch_torrent_info():
    torrents = await asyncio.get_running_loop().run_in_executor(None, lambda: qbt_client.torrents_info(status_filter='downloading'))
    return [{'name': torrent.name, 'progress': torrent.progress * 100} for torrent in torrents if torrent.progress < 1.0]

# Function to update Discord Rich Presence
async def update_discord_rpc():
    try:
        torrents = await fetch_torrent_info()
        activity = discord.Activity(name=f"{len(torrents)} active torrents", type=discord.ActivityType.watching)
        await bot.change_presence(activity=activity)
    except Exception as e:
        print(f"Failed to update RPC: {e}")

# Load and save last_message_id for Discord updates
def load_last_message_id():
    try:
        with open('last_message_id.txt', 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return None

def save_last_message_id(message_id):
    with open('last_message_id.txt', 'w') as file:
        file.write(str(message_id))

last_message_id = load_last_message_id()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print("------------------------------------------------")
    update_rpc_task.start()  # Start the Rich Presence update task
    scheduled_update.start()  # Start the scheduled chat update task

@tasks.loop(minutes=1)
async def update_rpc_task():
    await update_discord_rpc()

@tasks.loop(minutes=1)
async def scheduled_update():
    channel = bot.get_channel(config['update_channel_id'])
    if channel:
        await send_update(channel)

async def send_update(channel):
    global last_message_id
    torrents_list = await fetch_torrent_info()

    if torrents_list:
        embed = discord.Embed(title="Downloading Torrents", description="Current active downloads:")
        for torrent in torrents_list:
            embed.add_field(name=torrent['name'], value=f"{torrent['progress']:.2f}% completed", inline=False)
    else:
        embed = discord.Embed(title="Downloading Torrents", description="No torrents are currently downloading.")

    if last_message_id:
        try:
            message = await channel.fetch_message(last_message_id)
            await message.edit(embed=embed)
        except discord.NotFound:
            message = await channel.send(embed=embed)
            last_message_id = message.id
            save_last_message_id(last_message_id)  # Save new message ID
    else:
        message = await channel.send(embed=embed)
        last_message_id = message.id
        save_last_message_id(last_message_id)  # Save new message ID

# Bot token and run setup
bot.run(config['discord_token'])
