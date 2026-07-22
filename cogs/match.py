import datetime
import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import base_embed
import db

MAX_ATTACHMENT_MB = 25


class Match(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    match_group = app_commands.Group(name="match", description="Upload and review match demos")

    @match_group.command(name="upload", description="Attach a .dem file directly (works for smaller demos)")
    @app_commands.describe(demo="Your .dem file", map_name="Which map this was played on")
    async def upload(self, interaction: discord.Interaction, demo: discord.Attachment, map_name: str = None):
        if not demo.filename.lower().endswith(".dem"):
            await interaction.response.send_message(
                "That doesn't look like a `.dem` file — double check what you attached.", ephemeral=True
            )
            return

        size_mb = demo.size / (1024 * 1024)
        if size_mb > MAX_ATTACHMENT_MB:
            await interaction.response.send_message(
                f"That file is {size_mb:.1f}MB — Discord caps attachments at {MAX_ATTACHMENT_MB}MB on this server. "
                f"Upload it to Google Drive/Dropbox instead, set it to 'anyone with the link', "
                f"and use `/match link` with that link.",
                ephemeral=True,
            )
            return

        db.save_match(
            guild_id=interaction.guild_id,
            discord_id=interaction.user.id,
            filename=demo.filename,
            demo_url=demo.url,
            map_name=map_name,
            uploaded_at=datetime.datetime.utcnow().isoformat(),
        )

        embed = base_embed(
            "Match Uploaded",
            f"Saved **{demo.filename}**" + (f" on **{map_name}**" if map_name else "") + ".\n"
            f"This will feed stat parsing once Phase 4 is built.",
        )
        await interaction.response.send_message(embed=embed)

    @match_group.command(name="link", description="Submit a demo via an external link (for files over 25MB)")
    @app_commands.describe(url="Link to your demo file (Google Drive, Dropbox, etc. — set to 'anyone with the link')",
                            map_name="Which map this was played on")
    async def link(self, interaction: discord.Interaction, url: str, map_name: str = None):
        if not url.lower().startswith("http"):
            await interaction.response.send_message("That doesn't look like a valid link.", ephemeral=True)
            return

        db.save_match(
            guild_id=interaction.guild_id,
            discord_id=interaction.user.id,
            filename=url.split("/")[-1][:60],
            demo_url=url,
            map_name=map_name,
            uploaded_at=datetime.datetime.utcnow().isoformat(),
        )

        embed = base_embed(
            "Match Linked",
            f"Saved your demo link" + (f" on **{map_name}**" if map_name else "") + ".\n"
            f"This will feed stat parsing once Phase 4 is built.",
        )
        await interaction.response.send_message(embed=embed)

    @match_group.command(name="history", description="See your recently submitted matches")
    async def history(self, interaction: discord.Interaction):
        rows = db.get_recent_matches(interaction.user.id, limit=5)
        if not rows:
            await interaction.response.send_message("No matches submitted yet.", ephemeral=True)
            return

        lines = []
        for match_id, filename, map_name, uploaded_at in rows:
            date_str = uploaded_at.split("T")[0]
            map_str = f" — {map_name}" if map_name else ""
            lines.append(f"`#{match_id}` {filename}{map_str} ({date_str})")

        embed = base_embed("Your Recent Matches", "\n".join(lines))
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Match(bot))
