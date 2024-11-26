import os
import threading
from collections import deque
from threading import Lock

from discord.ext import commands
from discord import Intents
from flask import Flask, Response
from feedgen.feed import FeedGenerator

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FEED_CHANNELS_ENV = os.getenv('FEED_CHANNELS')
BASE_DOMAIN = os.getenv('BASE_URL')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))

if not DISCORD_TOKEN or not FEED_CHANNELS_ENV or not BASE_DOMAIN:
    print('Please set the DISCORD_TOKEN, FEED_CHANNELS, BASE_URL environment variables.')
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

# Initialize Flask app
app = Flask(__name__)

# Shared data structure for messages
messages_dict = {}  # key: feed_name, value: deque of messages
messages_lock = Lock()

# Initialize message deques for each feed
for feed_name in FEED_CHANNELS.keys():
    messages_dict[feed_name] = deque(maxlen=1000)  # Adjust maxlen as needed

def add_message_to_feed(feed_name, message):
    # Ignore messages without content
    if not message.content.strip():
        return
    # The first line is the title, rest is content
    lines = message.content.strip().split('\n', 1)
    if not lines:
        return  # Ignore empty messages
    title = lines[0]
    content = lines[1] if len(lines) > 1 else ''
    with messages_lock:
        messages_dict[feed_name].append({
            'title': title,
            'content': content,
            'link': f'https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id}',
            'pubDate': message.created_at,
            'author': message.author.name.capitalize()
        })

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
            add_message_to_feed(feed_name, message)
    print('Loaded previous messages.')

@bot.event
async def on_message(message):
    for feed_name, channel_id in FEED_CHANNELS.items():
        if message.channel.id == channel_id and not message.author.bot:
            add_message_to_feed(feed_name, message)
            break  # No need to check other feeds

@app.route('/rss/<feed_name>')
def rss_feed(feed_name):
    if feed_name not in messages_dict:
        return Response(f'Feed "{feed_name}" not found.', status=404)
    fg = FeedGenerator()
    fg.title(f'{feed_name} News Feed')
    fg.link(href=f'{BASE_DOMAIN}/rss/{feed_name}', rel='self')
    fg.description(f'A RSS feed Discord Channel Mirror "{feed_name}"')

    with messages_lock:
        msgs = sorted(messages_dict[feed_name], key=lambda x: x['pubDate'], reverse=True)

    print(f"Added {len(msgs)} messages to the feed for '{feed_name}'.")
    for msg in msgs:
        fe = fg.add_entry()
        fe.title(msg['title'])
        fe.content(msg['content'])
        fe.pubDate(msg['pubDate'])
        fe.dc_creator(name=msg['author'])

    rssfeed = fg.rss_str(pretty=True)
    return Response(rssfeed, mimetype='application/rss+xml')

def run_bot():
    bot.run(DISCORD_TOKEN)


bot_thread = threading.Thread(target=run_bot)
bot_thread.start()