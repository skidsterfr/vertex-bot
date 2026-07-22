"""
Simple SQLite layer for Vertex. Good enough through Phase 1 —
we can swap this for Postgres later without touching the cogs much,
since everything routes through the functions below.
"""
import sqlite3

DB_PATH = "vertex.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            announce_channel_id INTEGER,
            pushups_enabled INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_links (
            discord_id INTEGER PRIMARY KEY,
            steam_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def set_guild_channel(guild_id: int, channel_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO guild_config (guild_id, announce_channel_id)
        VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET announce_channel_id=excluded.announce_channel_id
    """, (guild_id, channel_id))
    conn.commit()
    conn.close()


def get_guild_config(guild_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT guild_id, announce_channel_id, pushups_enabled FROM guild_config WHERE guild_id=?",
        (guild_id,),
    )
    row = c.fetchone()
    conn.close()
    return row


def link_steam(discord_id: int, steam_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_links (discord_id, steam_id)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET steam_id=excluded.steam_id
    """, (discord_id, steam_id))
    conn.commit()
    conn.close()


def get_steam_id(discord_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT steam_id FROM user_links WHERE discord_id=?", (discord_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

    
def save_match(guild_id: int, discord_id: int, filename: str, demo_url: str, map_name: str, uploaded_at: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO matches (guild_id, discord_id, filename, demo_url, map_name, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (guild_id, discord_id, filename, demo_url, map_name, uploaded_at))
    conn.commit()
    conn.close()


def get_recent_matches(discord_id: int, limit: int = 5):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT match_id, filename, map_name, uploaded_at FROM matches
        WHERE discord_id=?
        ORDER BY match_id DESC
        LIMIT ?
    """, (discord_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows
