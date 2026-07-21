import discord
from discord import app_commands
from discord.ext import commands

import db
from utils.embeds import base_embed


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configure Vertex for this server")
    @app_commands.describe(announce_channel="Channel Vertex should post match/stat announcements in")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_cmd(self, interaction: discord.Interaction, announce_channel: discord.TextChannel):
        db.set_guild_channel(interaction.guild_id, announce_channel.id)
        embed = base_embed(
            "Setup complete",
            f"Announcements will post in {announce_channel.mention}.",
        )
        await interaction.response.send_message(embed=embed)

    @setup_cmd.error
    async def setup_cmd_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You need the **Manage Server** permission to run this.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Something went wrong running that command.", ephemeral=True
            )
            raise error

    @app_commands.command(name="link", description="Link your Steam account to Vertex")
    @app_commands.describe(steamid="Your SteamID64 (17-digit number)")
    async def link_cmd(self, interaction: discord.Interaction, steamid: str):
        db.link_steam(interaction.user.id, steamid)
        embed = base_embed(
            "Steam linked",
            f"Linked SteamID `{steamid}` to your Discord account.",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))
