# Gleam.io Giveaway Scraper

A CLI tool to scrape and interactively browse gleam.io giveaways with browser integration and CSV export.

## Features

- 🌐 Scrape all giveaways from gleam.io with automatic pagination
- 💾 Persistent caching with PostgreSQL (30-minute auto-refresh)
- 🎯 Interactive CLI with arrow key navigation
- 🔗 One-click browser opening for giveaways
- 📊 CSV export functionality
- 🐳 Docker-ready for future web app deployment

## Installation

### Requirements
- Python 3.9+
- PostgreSQL 12+ (optional - SQLite works for local development)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gleam-scraper.git
cd gleam-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env if you want to use PostgreSQL (optional - defaults to SQLite)
```

5. Initialize the database:
```bash
python -m src.cli --init-db
```

**Note:** The project defaults to SQLite (`gleam_scraper.db`) for local development. For production/Docker deployment, configure PostgreSQL in your `.env` file.

## Usage

### Run the interactive CLI
```bash
python -m src.cli
```

### Export to CSV
```bash
python -m src.cli --export-csv giveaways.csv
```

### Force refresh cache
```bash
python -m src.cli --force-refresh
```

### Use browser runtime (Playwright)
```bash
python -m src.cli --force-refresh --scraper-mode browser
```

### Show visible browser window (not headless)
```bash
python -m src.cli --force-refresh --scraper-mode browser --headed
```

### Show help
```bash
python -m src.cli --help
```

### 403 Troubleshooting
If you still get `403`/`Access Denied`, Gleam is blocking automated access from your environment.
The scraper now uses browser-like headers, retries, and optional browser fallback, but access can still be denied by server-side controls.

## Interactive Navigation

- **Arrow keys**: Navigate through the full giveaway list (scrollable)
- **Enter**: Select giveaway and choose an action (open/details/back)
- **Esc**: Exit dialogs and quit from the main list

## Configuration

Edit `.env` to customize:
- `DATABASE_URL`: PostgreSQL connection string
- `CACHE_TTL`: Cache timeout in minutes (default: 30)
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds (default: 10)
- `REQUEST_DELAY_SECONDS`: Delay between page fetches (default: 1.0)
- `MAX_RETRIES`: Retry count for transient HTTP failures (default: 3)
- `SCRAPER_MODE`: `auto`, `requests`, or `browser` (default: `auto`)
- `PLAYWRIGHT_HEADLESS`: Run browser headless (`true`/`false`)
- `PLAYWRIGHT_BROWSER`: `chromium`, `firefox`, or `webkit`
- `PLAYWRIGHT_WAIT_UNTIL`: page load target (`domcontentloaded`, `load`, `networkidle`, `commit`)
- `PLAYWRIGHT_POST_NAV_WAIT_MS`: extra JS settle time after navigation
- `PLAYWRIGHT_TIMEOUT_MULTIPLIER`: multiplies `REQUEST_TIMEOUT` for browser navigation

If Gleam returns 403 in request mode, `SCRAPER_MODE=auto` can fall back to a real browser fetcher.
Install browser support with:

```bash
pip install playwright
python -m playwright install chromium
```

## Docker Usage (Future)

```bash
docker build -t gleam-scraper .
docker run --env-file .env gleam-scraper
```

## Development

### Run tests
```bash
pytest -v
```

### Run tests with coverage
```bash
pytest --cov=src tests/
```

### Format code
```bash
black src/ tests/
```

### Lint
```bash
flake8 src/ tests/
```

## Architecture

The project is structured for easy migration to a web app:

- **src/scraper.py**: Web scraping logic (reusable)
- **src/database.py**: Data models and ORM (reusable)
- **src/cache.py**: Caching layer (reusable)
- **src/ui.py**: CLI/TUI components
- **src/cli.py**: CLI entry point

## Programmatic API (for separate web repo)

To integrate this project into a separate web application repository, use the stable public package API:

```python
from gleam_scraper import init_database, list_competitions, competitions_to_dicts

init_database()
competitions = list_competitions(force_refresh=False, scraper_mode="auto")
payload = competitions_to_dicts(competitions)
```

The `gleam_scraper` package exposes:
- `init_database()`
- `list_competitions(...)`
- `refresh_competitions(...)`
- `competitions_to_dicts(...)`

This keeps the scraper as the single source of truth while your web repo focuses on API/UI concerns.

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
