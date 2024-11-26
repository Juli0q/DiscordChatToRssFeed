# app.py

import os
import sqlite3
from flask import Flask, Response
from feedgen.feed import FeedGenerator
from content_encoded_extension import ContentEncodedExtension
from dccreator_extension import DCCreatorEntryExtension  # Import the custom extension

# Load environment variables
FEED_CHANNELS_ENV = os.getenv('FEED_CHANNELS')
BASE_DOMAIN = os.getenv('BASE_URL')

if not FEED_CHANNELS_ENV or not BASE_DOMAIN:
    print('Please set the FEED_CHANNELS and BASE_URL environment variables.')
    exit(1)

# Parse FEED_CHANNELS environment variable into a list of feed names
FEED_NAMES = []
try:
    for pair in FEED_CHANNELS_ENV.split(','):
        name, _ = pair.split('=')
        FEED_NAMES.append(name.strip())
except ValueError:
    print('Error parsing FEED_CHANNELS environment variable. Please use the format feedName=channelID,anotherFeedName=anotherChannelID')
    exit(1)

# Initialize Flask app
app = Flask(__name__)

# Initialize SQLite database
conn = sqlite3.connect('messages.db', check_same_thread=False)
c = conn.cursor()

@app.route('/<feed_name>')
def rss_feed(feed_name):
    if feed_name not in FEED_NAMES:
        return Response(f'Feed "{feed_name}" not found.', status=404)

    fg = FeedGenerator()
    fg.title(f'{feed_name} News Feed')
    fg.link(href=f'{BASE_DOMAIN}/{feed_name}', rel='self')
    fg.description(f'A RSS feed Discord Channel Mirror "{feed_name}"')

    c.execute("SELECT title, content, link, pubDate, author FROM messages WHERE feed_name = ? ORDER BY pubDate DESC", (feed_name,))
    msgs = c.fetchall()

    print(f"Showing {len(msgs)} messages to response of feed '{feed_name}'.")

    for msg in msgs:
        fe = fg.add_entry()
        fe.register_extension('content', ContentEncodedExtension)
        fe.register_extension('dccreator', DCCreatorEntryExtension)
        fe.title(msg[0])
        fe.pubDate(msg[3])

        # Set the creator using the custom extension
        fe.dccreator.set_creator(msg[4])

        # Set the 'content:encoded' element
        fe.content.set_content_encoded(msg[1])

    rssfeed = fg.rss_str(pretty=True)
    return Response(rssfeed, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
