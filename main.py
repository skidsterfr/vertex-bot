import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from keep_alive import keep_alive
import db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True


class VertexBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Create/verify database tables on boot
        db.init_db()

        # Load feature cogs
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.config")
        await self.load_extension("cogs.economy")

        # Push slash commands to Discord
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")


bot = VertexBot()


@bot.event
async def on_ready():
    print(f"Vertex is online as {bot.user} (ID: {bot.user.id})")


if __name__ == "__main__":
    keep_alive()  # tiny web server so Render has something to ping
    bot.run(TOKEN)
