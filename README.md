# Sprite Exchange

Sprite Exchange is a single-file FastAPI application for comparing Fortnite.GG sprite collections and preparing exchanges between players.

The backend, HTML, CSS, JavaScript, Fortnite.GG parser, local persistence, exchange optimizer, matrix view, and sprite grids are all contained in one Python file: `app.py`.

## Features

### Player management

- Add a player using the numeric ID from a Fortnite.GG URL such as:

  ```text
  https://fortnite.gg/sprites?id=3908468
  ```

- Fetch the player name, official ownership counters, sprite statuses, and sprite images.
- Refresh one player or refresh all players.
- Select or deselect players for exchange generation.
- Open the original Fortnite.GG page from each player card.
- Display owned and mastered progress bars.
- Keep the player list and interface state in the browser with `localStorage`.

### Collection matrix

The **Matrix** tab displays one row and one column per player.

- A cell at row `A`, column `B` contains the number of sprites player A owns and player B is missing.
- A diagonal cell contains the number of sprites owned by that player.
- A cell displays `?` when one or both players do not have valid refreshed data.
- Clicking a valid cell opens a sprite grid below the matrix.
- A diagonal cell shows every sprite owned by that player.
- An off-diagonal cell shows sprites owned by the row player and missing from the column player.
- The sprite grid can be filtered between:
  - **All**
  - **Local only**

The matrix and the selected sprite grid are recalculated whenever player data changes.

### Exchange generation

- Generate a randomized best partial exchange solution for selected players.
- Each player gives at most one sprite.
- Each player receives at most one sprite.
- A player may only give, only receive, do both, or remain outside the solution.
- Every proposed sprite is owned by the giver and missing from the receiver.
- The algorithm maximizes the total number of valid transfers.
- Equivalent maximum solutions are randomized, so repeated generations can produce different proposals.
- Exchanges are displayed as responsive cards with:
  - sprite image;
  - sprite name;
  - giver;
  - receiver.

### Local exchange confirmation

Each exchange card has an **Exchanged** button.

When pressed:

- the receiver is marked as owning that sprite locally;
- the player counters are updated;
- the matrix is updated;
- the selected matrix sprite grid is updated;
- the local declaration is persisted in `localStorage`.

A locally declared sprite remains owned after refreshing the player from Fortnite.GG when the source still reports it as missing.

When Fortnite.GG later reports the sprite as owned or mastered, the local override is automatically removed because the source has become authoritative again.

Sprites that are owned only through a local declaration display a **Local only** badge in the matrix sprite grid.

## Application tabs

The interface contains three tabs:

1. **Players** — add, select, refresh, and remove players.
2. **Matrix** — compare collections and inspect matching sprites.
3. **Exchanges** — generate and confirm exchanges.

The active tab is remembered in the browser.

## Architecture

The browser does not request Fortnite.GG directly. It calls the local FastAPI endpoint:

```text
GET /api/player/{player_id}
```

FastAPI then requests:

```text
https://fortnite.gg/sprites?id={player_id}
```

The server parses and validates the HTML before returning JSON to the interface. This avoids browser CORS restrictions.

The application uses `curl_cffi` to imitate a browser network fingerprint. An optional Playwright/Chromium fallback can be used when the direct fetch is rejected.

## Requirements

- Python 3.10 or newer
- Internet access from the server

Recommended dependencies:

```text
fastapi
uvicorn[standard]
curl_cffi
beautifulsoup4
```

Optional Chromium fallback:

```text
playwright
```

`httpx` is not required.

## Installation

Create a virtual environment.

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

Install the required packages:

```bash
pip install fastapi "uvicorn[standard]" curl_cffi beautifulsoup4
```

Optional Playwright fallback:

```bash
pip install playwright
playwright install chromium
```

On some Linux servers, Chromium also needs its system dependencies:

```bash
playwright install --with-deps chromium
```

## Run locally

Place the application in a file named `app.py`, then run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8000
```

You can also launch it explicitly with Uvicorn:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

The file uses this production-compatible entry point:

```python
if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
```

## Minimal repository

```text
sprite-exchange/
├── app.py
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

Add Playwright only when required:

```text
playwright
```

## Deploy on Render

Create a Render Web Service connected to the Git repository.

### Build command

```bash
pip install -r requirements.txt
```

### Start command

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Make sure `app.py` is at the repository root.

A recent stable Python version such as Python 3.12 or 3.13 is recommended. It can be configured with a `.python-version` file:

```text
3.12
```

When Playwright is required, the build command can be extended to:

```bash
pip install -r requirements.txt && playwright install --with-deps chromium
```

Cloud hosting providers may use IP ranges that Fortnite.GG blocks. If local fetching works but the hosted deployment receives HTTP 403 responses, this may be an upstream datacenter-IP restriction rather than a FastAPI error.

## Deploy on Railway

Connect the repository and use:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Generate a public domain in the Railway networking settings.

## API

### `GET /`

Serves the complete application interface.

### `GET /api/player/{player_id}`

Fetches, parses, and validates a Fortnite.GG sprite page.

Example:

```text
GET /api/player/3908468
```

Use the optional `force=true` query parameter to bypass the short-lived in-memory cache:

```text
GET /api/player/3908468?force=true
```

Example response shape:

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

Supported sprite statuses:

```text
missing
owned
mastered
unreleased
```

## Data persistence

Most application state is stored in the browser through `localStorage`:

- players;
- selected players;
- last generated result;
- active tab;
- locally confirmed ownership overrides.

Consequences:

- each browser has its own data;
- deploying a new server version does not normally erase browser data;
- another device or browser will not automatically share the same state;
- clearing browser site data removes players and local exchange confirmations.

The FastAPI response cache is held only in server memory and is lost when the process restarts.

## Ownership source rules

For each sprite, the effective ownership can come from either:

1. Fortnite.GG;
2. a local **Exchanged** confirmation.

The merge behavior is:

- remote `owned` or `mastered` always counts as source-confirmed ownership;
- remote `missing` plus a local override counts as locally declared ownership;
- after refresh, a local override is retained only while the remote source still says `missing`;
- once the remote source confirms ownership, the override is removed automatically.

This allows several games to be organized quickly even when Fortnite.GG has not yet synchronized the latest exchanges.

## Exchange algorithm

The current optimizer models players as potential givers and receivers in a bipartite graph.

An edge from player A to player B exists when A owns at least one sprite that B is missing.

A randomized maximum matching is computed so that:

- each giver is used at most once;
- each receiver is used at most once;
- the number of transfers is maximized;
- players are not required to form closed cycles;
- a valid partial solution is returned even when not every selected player can participate.

After player pairs are chosen, one compatible sprite is selected randomly for each transfer.

## Troubleshooting

### `ModuleNotFoundError`

Install all dependencies from `requirements.txt` and verify that unused imports such as `httpx` are not left in `app.py`.

### Render cannot import `app`

Confirm that:

- the file is named `app.py`;
- it is at the repository root;
- it contains `app = FastAPI(...)`;
- the start command is:

  ```bash
  uvicorn app:app --host 0.0.0.0 --port $PORT
  ```

### Fortnite.GG returns HTTP 403

Confirm that `curl_cffi` is installed. If it still fails, install Playwright and Chromium. A cloud-provider IP may also be blocked upstream.

### Player data looks stale

Use the refresh button. The frontend requests a forced refresh when appropriate, and the backend supports `?force=true`.

### Locally exchanged sprites remain after refresh

This is intentional while Fortnite.GG still reports them as missing. They disappear from the local-only list automatically once the remote source confirms ownership.

### Matrix displays `?`

At least one of the two players has not been refreshed successfully or does not have a valid sprite list.

## Limitations

- The parser depends on Fortnite.GG HTML and may require maintenance if the site changes.
- Fortnite.GG can reject automated requests or cloud-hosting IP addresses.
- Browser data is local to one browser profile.
- Local exchange confirmations are not synchronized between users or devices.
- There is no authentication or shared database.
- The application is intended as a lightweight coordination tool, not as an authoritative inventory system.

## License and attribution

Choose and add an appropriate license before distributing the project publicly.

Fortnite, Fortnite.GG, sprite names, and sprite artwork belong to their respective owners. This project is an independent utility and is not affiliated with or endorsed by Epic Games or Fortnite.GG.