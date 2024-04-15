# Torrent-Tracker-Bot
# Discord Torrent Update Bot

This bot uses the Discord and qBittorrent APIs to update a specified Discord channel with information about downloading torrents.

## Setup

1. Install the required libraries using pip:
pip install discord.py qbittorrent-api

2. Replace the placeholders in the code with your own values:
- Replace `'localhost'` with the IP address of your qBittorrent server.
- Replace `'admin'` with your qBittorrent username.
- Replace `'yourpassword'` with your qBittorrent password.
- Set `update_channel_id` to the ID of the Discord channel where you want the updates to be sent.
- Replace `'your_bot_token'` with your Discord bot token.

3. Run the bot:
TorrentTrackerBot.py


## Features

- Automatically updates the specified Discord channel with information about downloading torrents.
- Uses qBittorrent API to fetch torrent information.
- Uses Discord API to send updates to a specific channel.
