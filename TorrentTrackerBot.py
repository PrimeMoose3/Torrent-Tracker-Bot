import discord
from discord.ext import commands, tasks
import qbittorrentapi
import os

# Initialize the qBittorrent client
qbt_client = qbittorrentapi.Client(
    host='localhost', port=8080, 
    username='admin', 
    password='yourpassword'  # Make sure to secure your password properly
)

# Initialize Discord Intents and Bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)

# Function to update downloading torrents
def update_downloading_torrents():
    try:
        torrents = qbt_client.torrents_info(status_filter='downloading')
        return [{'name': torrent.name, 'progress': torrent.progress * 100} for torrent in torrents if torrent.progress < 1.0]
    except qbittorrentapi.APIError as e:
        print(f"API error occurred while fetching torrents: {e}")
        return []
    except Exception as e:
        print(f"Failed to fetch torrents due to an unexpected error: {e}")
        return []

# Load last_message_id from file
def load_last_message_id():
    try:
        with open('last_message_id.txt', 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return None

# Save last_message_id to file
def save_last_message_id(message_id):
    with open('last_message_id.txt', 'w') as file:
        file.write(str(message_id))

last_message_id = load_last_message_id()  # Load last message ID at startup
update_channel_id = CHANNELID  # Set your channel ID here

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print("------------------------------------------------")
    scheduled_update.start()

@tasks.loop(minutes=1)
async def scheduled_update():
    channel = bot.get_channel(update_channel_id)
    if channel:
        await send_update(channel)

async def send_update(channel):
    global last_message_id
    torrents_list = update_downloading_torrents()

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
bot.run('your_bot_token')
