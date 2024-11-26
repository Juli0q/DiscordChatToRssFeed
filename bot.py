# bot.py
import os
import asyncio
import sqlite3
from discord.ext import commands
from discord import Intents

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FEED_CHANNELS_ENV = os.getenv('FEED_CHANNELS')

if not DISCORD_TOKEN or not FEED_CHANNELS_ENV:
    print('Please set the DISCORD_TOKEN and FEED_CHANNELS environment variables.')
    exit(1)

# Parse FEED_CHANNELS environment variable into a dictionary {feed_name: channel_id}
FEED_CHANNELS = {}
try:
    for pair in FEED_CHANNELS_ENV.split(','):
        name, cid = pair.split('=')
        FEED_CHANNELS[name.strip()] = int(cid.strip())
except ValueError:
    print('Error parsing FEED_CHANNELS environment variable. Please use the format feedName=channelID,anotherFeedName=anotherChannelID')
    exit(1)

# Initialize the bot
intents = Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize SQLite database
conn = sqlite3.connect('messages.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (feed_name TEXT, title TEXT, content TEXT, link TEXT, pubDate TEXT, author TEXT)''')
conn.commit()

def add_message_to_db(feed_name, message):
    # Ignore messages without content
    if not message.content.strip():
        return
    # The first line is the title, rest is content
    lines = message.content.strip().split('\n', 1)
    if not lines:
        return  # Ignore empty messages
    title = lines[0]
    content = lines[1] if len(lines) > 1 else ''
    link = f'https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id}'
    pubDate = message.created_at.isoformat()
    author = message.author.name.capitalize()

    c.execute("INSERT INTO messages (feed_name, title, content, link, pubDate, author) VALUES (?, ?, ?, ?, ?, ?)",
              (feed_name, title, content, link, pubDate, author))
    conn.commit()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for feed_name, channel_id in FEED_CHANNELS.items():
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f'Channel with ID {channel_id} for feed "{feed_name}" not found.')
            continue
        # Fetch previous messages
        async for message in channel.history(limit=None, oldest_first=True):
            if message.author.bot:
                continue  # Skip messages from bots
            add_message_to_db(feed_name, message)
    print('Loaded previous messages.')

@bot.event
async def on_message(message):
    for feed_name, channel_id in FEED_CHANNELS.items():
        if message.channel.id == channel_id and not message.author.bot:
            add_message_to_db(feed_name, message)
            break  # No need to check other feeds

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
