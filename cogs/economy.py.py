import random
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import base_embed
import db

STEAM_INVENTORY_URL = "https://steamcommunity.com/inventory/{steamid}/730/2?l=english&count=200"
STEAM_PRICE_URL = "https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item}"


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="View your CS2 inventory summary")
    async def inventory(self, interaction: discord.Interaction):
        steam_id = db.get_steam_id(interaction.user.id)
        if not steam_id:
            await interaction.response.send_message(
                "Link your Steam account first with `/link`.", ephemeral=True
            )
            return

        await interaction.response.defer()
        url = STEAM_INVENTORY_URL.format(steamid=steam_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send(
                        "Couldn't read that inventory — make sure it's set to **Public** "
                        "in Steam privacy settings (Steam > Privacy Settings > Inventory)."
                    )
                    return
                data = await resp.json()

        assets = data.get("assets", [])
        if not assets:
            await interaction.followup.send("That inventory looks empty (or private).")
            return

        embed = base_embed(
            "Inventory Summary",
            f"**{len(assets)}** items found for SteamID `{steam_id}`.\n"
            f"Use `/price [item name]` to check what any individual item is worth.",
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="price", description="Look up the current market price of a CS2 item")
    @app_commands.describe(item="Exact market name, e.g. 'AK-47 | Redline (Field-Tested)'")
    async def price(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer()
        url = STEAM_PRICE_URL.format(item=item.replace(" ", "%20"))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        if not data.get("success"):
            await interaction.followup.send(f"Couldn't find a price for `{item}` — check the exact spelling.")
            return

        embed = base_embed(item)
        embed.add_field(name="Lowest Price", value=data.get("lowest_price", "N/A"))
        embed.add_field(name="Median Price", value=data.get("median_price", "N/A"))
        embed.add_field(name="24h Volume", value=data.get("volume", "N/A"))
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="tradeup", description="Calculate the average float going into a trade-up")
    @app_commands.describe(floats="10 input floats, comma-separated, e.g. 0.10,0.12,0.15,...")
    async def tradeup(self, interaction: discord.Interaction, floats: str):
        try:
            values = [float(x.strip()) for x in floats.split(",")]
        except ValueError:
            await interaction.response.send_message(
                "Floats must be numbers separated by commas.", ephemeral=True
            )
            return

        if len(values) != 10:
            await interaction.response.send_message(
                "A trade-up needs exactly 10 input floats.", ephemeral=True
            )
            return

        avg = sum(values) / len(values)
        embed = base_embed(
            "Trade-Up Calculator",
            f"Average input float: **{avg:.4f}**\n\n"
            f"To get the exact output float: multiply this average by "
            f"(target skin's max float − min float), then add the min float back.",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin — or two, for gambling-site mode decisions")
    @app_commands.describe(gamble="Flip two coins back to back for jackpot/crazy mode decisions")
    async def coinflip(self, interaction: discord.Interaction, gamble: bool = False):
        if not gamble:
            result = random.choice(["Heads", "Tails"])
            embed = base_embed("Coin Flip", f"**{result}**")
        else:
            flip1 = random.choice(["Heads", "Tails"])
            flip2 = random.choice(["Heads", "Tails"])
            mode1 = "Jackpot Mode" if flip1 == "Heads" else "Regular Mode"
            mode2 = "Crazy Mode" if flip2 == "Heads" else "Regular Mode"
            embed = base_embed(
                "Coin Flip — Gambling Mode",
                f"Flip 1: **{flip1}** → {mode1}\nFlip 2: **{flip2}** → {mode2}",
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))