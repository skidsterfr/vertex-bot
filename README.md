# Vertex

Phase 0 (`/ping`) + Phase 1 (`/setup`, `/link`) starter, built with Claude.

## Local files
- `main.py` — bot entry point, loads cogs, syncs slash commands
- `keep_alive.py` — tiny web server so Render's free tier has something to ping
- `db.py` — SQLite storage for per-server config and Steam links
- `utils/embeds.py` — shared embed styling so every command looks consistent
- `cogs/general.py` — `/ping`
- `cogs/config.py` — `/setup`, `/link`

## Running it
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and paste in your real bot token
3. `python main.py`

See the chat for the full Render deployment walkthrough.
