import os
import discord
import asyncio
import praw
from datetime import datetime
from server import keep_alive

intents = discord.Intents.default()

client = discord.Client(intents=intents)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

CHANNEL_ID = 1400741869587140618
SUBREDDIT_NAME = "Guildwars2"
posted_posts = set()

@client.event
async def on_ready():
    print(f"✅ Bot ist online als {client.user}")
    client.loop.create_task(check_subreddit())

async def check_subreddit():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Channel nicht gefunden!")
        return

    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    while not client.is_closed():
        print("🔍 Suche nach neuen Beiträgen...")
        try:
            for post in subreddit.new(limit=5):
                if post.id not in posted_posts:
                    posted_posts.add(post.id)

                    description = post.selftext[:397] + "..." if post.selftext and len(post.selftext) > 400 else post.selftext
                    if getattr(post, "spoiler", False):
                        description = f"||{description}||"

                    embed = discord.Embed(
                        title=post.title,
                        url=f"https://reddit.com{post.permalink}",
                        description=description or " ",
                        color=discord.Color.orange()
                    )
                    embed.set_author(name=f"u/{post.author}")
                    embed.set_footer(text=f"r/{SUBREDDIT_NAME}")
                    embed.timestamp = datetime.utcfromtimestamp(post.created_utc)

                    if hasattr(post, "url") and post.url.endswith((".jpg", ".png", ".jpeg", ".gif")):
                        embed.set_image(url=post.url)

                    await channel.send(embed=embed)
        except Exception as e:
            print(f"❌ Fehler beim Abrufen: {e}")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv("DISCORD_TOKEN"))

