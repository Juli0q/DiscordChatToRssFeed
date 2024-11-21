# Discord Chat to RSS Feed

This is a simple script that will take a Discord chat and convert it to an RSS feed.

## Environment Variables
- `FEED_CHANNELS` - A comma separated list of channel IDs and their names. The format is `channel_id=channel_name`. For example, `general=<ChannelID>,general2=<ChannelID>`.
- `DISCORD_TOKEN` - The Discord bot token.
- `DEFAULT_MAIL` - The email address to use for every author in the feed. RSS needs a Email address for the author field.
- `BASE_URL` - The base URL for the RSS feed. This is used to generate the links for the feed.
- `PORT` - The port to run the server on. Default is 5000.
- `HOST` - The host to run the server on. Default is 0.0.0.0.

## Usage
Docker Command
```bash
docker run ghcr.io/juli0q/discord-chat-rss-feed:latest -e FEED_CHANNELS="general=<ChannelID>,general2=<ChannelID>" -e DISCORD_TOKEN="<DiscordToken>" -e DEFAULT_MAIL="<Email>" -e BASE_URL="<URL>"
```

Docker Compose
```yaml
version: '3.7'
services:
  discord-chat-rss-feed:
    image: ghcr.io/juli0q/discord-chat-rss-feed:latest
    environment:
      - FEED_CHANNELS="general=<ChannelID>,general2=<ChannelID>"
      - DISCORD_TOKEN="<DiscordToken>"
      - DEFAULT_MAIL="<Email>"
      - BASE_URL="<URL>"
    ports:
      - "3000:5000"
```

With this example the 2 feeds will be available at:
- `http://localhost:3000/rss/general`
- `http://localhost:3000/rss/general2`