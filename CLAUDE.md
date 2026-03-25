# MusicMind MCP

## Quick Commands
- `uv run python -m musicmind.server` — Start MCP server (stdio)
- `uv run python -m musicmind.setup` — Run one-time Apple Music OAuth setup
- `uv run pytest` — Run tests
- `uv run ruff check src/` — Lint

## Architecture
Python FastMCP server connecting Claude to Apple Music API. Three layers:
1. **API Client** (client.py) — async httpx client for api.music.apple.com, 25+ endpoints
2. **Persistence** (db/) — SQLite cache for listening history, song metadata, taste profiles
3. **Taste Engine** (engine/) — algorithmic profile building + candidate scoring from metadata

Tools are organized by domain: library, catalog, playback, manage, taste, recommend.

## Code Style
- All tool inputs: Pydantic BaseModel with Field() descriptions
- All tool names: musicmind_{action}_{resource} in snake_case
- Async everywhere for network calls
- Type hints on all functions
- No stdout logging (stderr only — MCP requirement)
- Genre handling: always split hierarchical genres (e.g., "Italian Hip-Hop/Rap" → ["Italian Hip-Hop/Rap", "Hip-Hop/Rap"])

## API Auth
- Developer Token: ES256 JWT signed with .p8 private key, 6-month expiry
- Music User Token: obtained via MusicKit JS OAuth browser flow (setup.py)
- Config stored at ~/.config/musicmind/config.json (permissions 600)
- Both tokens sent as headers: Authorization: Bearer {dev_token}, Music-User-Token: {user_token}

## Key Apple Music API Notes
- Library songs lack play count — only available via native MusicKit on iOS/macOS
- Use ?include=catalog on library requests to get full catalog metadata (genres, ISRC, editorial notes)
- Recently played tracks: max 50, paginated with offset in batches of 10, no timestamps
- Heavy rotation: often returns empty for light listeners — don't rely on it exclusively
- Ratings: value 1 = love, -1 = dislike. PUT to set, DELETE to remove.
- Rate limits: ~20 req/sec (undocumented), handle 429 with exponential backoff
- Artist views parameter: top-songs, similar-artists, featured-playlists, latest-release, full-albums
- Storefront: default "it" (Italy), auto-detect via /v1/me/storefront

## Known Issues
[Empty — add issues here as discovered]

## Dependencies
- mcp — FastMCP server framework
- httpx — async HTTP client
- aiosqlite — async SQLite driver
- sqlalchemy — query building (Core only, no ORM)
- pyjwt[crypto] + cryptography — ES256 JWT for Apple developer tokens
- numpy — vector operations for taste profile scoring
- pydantic — input validation for all MCP tools
- ruff — linting
- pytest + pytest-asyncio — testing
