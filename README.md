# Sprite Exchange

Sprite Exchange is a small FastAPI web application for organizing Fortnite.GG sprite exchanges between players.

The project intentionally fits in a **single Python file**: the FastAPI backend, HTML, CSS, JavaScript, data parser, local persistence logic, and exchange-generation algorithm are all bundled in `sprite_exchange_app_v8.py`.

## Features

- Add players using their Fortnite.GG sprite-page ID.
- Fetch player names, sprite ownership, and mastered counts from Fortnite.GG.
- Display ownership and mastery progress for every player.
- Refresh one player or all players.
- Select the players participating in a session.
- Generate valid randomized exchange cycles.
- Ensure each participating player gives at most one sprite and receives at most one sprite.
- Maximize the number of participating players.
- Display exchanges as responsive cards with sprite artwork and donor/receiver names.
- Keep the player list and UI state in the browser through `localStorage`.
- Provide separate **Players** and **Trades** tabs.
- Cache fetched Fortnite.GG pages briefly in server memory to reduce repeated requests.

## How it works

The browser never contacts Fortnite.GG directly. It calls the local FastAPI endpoint:

```text
GET /api/player/{player_id}
```

FastAPI then fetches the corresponding page:

```text
https://fortnite.gg/sprites?id={player_id}
```

The backend parses the returned HTML and sends validated JSON to the interface. This avoids browser CORS restrictions.

The application first tries `curl_cffi`, which can imitate a browser TLS fingerprint. If that fails and Playwright is installed, it falls back to a headless Chromium browser.

## Requirements

- Python 3.10 or newer
- Internet access from the machine running the server

Recommended Python packages:

```text
fastapi
uvicorn[standard]
curl_cffi
beautifulsoup4
```

Optional fallback:

```text
playwright
```

## Installation

Create and activate a virtual environment.

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install fastapi "uvicorn[standard]" curl_cffi beautifulsoup4
```

Optional Playwright fallback:

```bash
pip install playwright
playwright install chromium
```

On Linux servers, Chromium may also require system dependencies:

```bash
playwright install --with-deps chromium
```

## Run locally

With the application file named `sprite_exchange_app_v8.py`:

```bash
python sprite_exchange_app_v8.py
```

Open:

```text
http://127.0.0.1:8000
```

You can also start it explicitly with Uvicorn:

```bash
uvicorn sprite_exchange_app_v8:app --host 127.0.0.1 --port 8000
```

## Deploy online

For a hosted deployment, bind Uvicorn to `0.0.0.0` and use the port supplied by the hosting platform.

Example start command:

```bash
uvicorn sprite_exchange_app_v8:app --host 0.0.0.0 --port $PORT
```

### Minimal repository structure

```text
sprite-exchange/
├── sprite_exchange_app_v8.py
├── requirements.txt
└── README.md
```

Suggested `requirements.txt`:

```text
fastapi
uvicorn[standard]
curl_cffi
beautifulsoup4
```

Add Playwright only when the `curl_cffi` path is not sufficient:

```text
playwright
```

### Render

Create a Web Service from the Git repository.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn sprite_exchange_app_v8:app --host 0.0.0.0 --port $PORT
```

When Playwright is required, use a build command such as:

```bash
pip install -r requirements.txt && playwright install --with-deps chromium
```

### Railway

Deploy the Git repository and configure this start command:

```bash
uvicorn sprite_exchange_app_v8:app --host 0.0.0.0 --port $PORT
```

Generate a public domain from the Railway networking settings.

## API

### `GET /`

Serves the complete web interface.

### `GET /api/player/{player_id}`

Fetches and parses a Fortnite.GG player page.

Example:

```text
GET /api/player/3908468
```

Optional query parameter:

```text
force=true
```

This bypasses the short-lived in-memory cache.

Example response structure:

```json
{
  "id": "3908468",
  "cached": false,
  "method": "curl_cffi",
  "player": {
    "id": "3908468",
    "name": "Player name",
    "stats": {
      "owned": 45,
      "mastered": 14,
      "total": 91
    },
    "sprites": [
      {
        "name": "Sprite name",
        "imageUrl": "https://fortnite.gg/...",
        "status": "owned"
      }
    ],
    "warnings": [],
    "updatedAt": "2026-01-01T12:00:00+00:00"
  }
}
```

Possible sprite statuses:

```text
missing
owned
mastered
unreleased
```

### `GET /health`

Simple health check:

```json
{
  "ok": true,
  "cached_players": 2
}
```

## Exchange algorithm

The interface builds a directed compatibility graph:

- an edge from player A to player B exists when A owns at least one sprite that B is missing;
- each selected player can give at most one sprite;
- each selected player can receive at most one sprite;
- self-transfers are forbidden;
- valid participating players form closed exchange cycles.

The generator uses a maximum-assignment approach to maximize the number of participating players. Random tie-breaking is applied so repeated generations can produce different valid proposals when several equivalent solutions exist.

## Data persistence

Player data is stored in the browser with `localStorage`.

Consequences:

- every browser has its own player list;
- redeploying or restarting the server does not erase the browser list;
- using another device or browser does not automatically share the same list;
- clearing browser storage removes saved players and UI state.

The FastAPI cache is only held in process memory and is cleared when the server restarts.

## Troubleshooting

### Fortnite.GG returns `403 Forbidden`

Install and use `curl_cffi`:

```bash
pip install curl_cffi
```

If the hosting provider's IP range is blocked, trying another provider may help. Datacenter IP filtering can differ between Render, Railway, Fly.io, and a self-hosted server.

### The fallback Chromium browser is unavailable

Install Playwright and Chromium:

```bash
pip install playwright
playwright install chromium
```

For Linux servers:

```bash
playwright install --with-deps chromium
```

### A player page is fetched but rejected as inconsistent

The parser validates the number of released sprites and the official ownership counters before accepting the response. Fortnite.GG markup can change over time, so a frontend change may require updating `_parse_player_html`.

### The application works locally but fails in production

Likely causes include:

- the hosting provider's IP being blocked by Fortnite.GG;
- missing `curl_cffi` or Playwright dependencies;
- Chromium system libraries not being installed;
- the server being started on `127.0.0.1` instead of `0.0.0.0`;
- the hosting platform not passing the expected `$PORT` variable.

## Security and operational notes

- The player ID is validated before being used in an outbound request.
- The backend only fetches the fixed Fortnite.GG sprite URL pattern.
- No authentication is included.
- No central database is included.
- The in-memory cache is intentionally short-lived.
- Do not expose development servers directly to the public internet without a production process manager or hosting platform.
- Add rate limiting before opening the service to a large audience.

## Third-party service notice

This project is not affiliated with, endorsed by, or sponsored by Epic Games or Fortnite.GG.

It depends on the current public HTML structure and availability of Fortnite.GG. That structure may change without notice, and automated access may be restricted. Review the site's applicable terms and avoid excessive request rates.

## License

No license is currently included. Add a `LICENSE` file before distributing or publishing the project if you want to define reuse permissions explicitly.