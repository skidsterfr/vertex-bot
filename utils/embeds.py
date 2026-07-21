import discord

BRAND_COLOR = 0xFF8A3D  # keeps every embed looking like the same bot


def base_embed(title: str, description: str = None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=BRAND_COLOR)
    embed.set_footer(text="Vertex")
    return embed
