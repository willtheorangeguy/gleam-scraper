# Gleam.io Giveaway Scraper — Quickstart

## 1. Install

```bash
git clone https://github.com/willtheorangeguy/gleam-scraper.git
cd gleam-scraper

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Requires Python 3.9+.

## 2. Configure

```bash
cp .env.example .env
```

You can leave it as is. Without `DATABASE_URL`, the project uses SQLite at
`gleam_scraper.db`, which is the right choice for local use — PostgreSQL is for deployment.

## 3. Initialise the database

```bash
python -m src.cli --init-db
```

## 4. Browse

```bash
python -m src.cli
```

| Key | Action |
|---|---|
| Arrow keys | Move through the list, which scrolls |
| `Enter` | Select a giveaway, then choose open, details, or back |
| `Esc` | Leave a dialog, or quit from the main list |

## If you get `403` or `Access Denied`

Expected, not a misconfiguration. Gleam blocks automated HTTP access. Install browser support
and use it:

```bash
pip install playwright
python -m playwright install chromium

python -m src.cli --force-refresh --scraper-mode browser
```

Add `--headed` to watch what the browser is doing.

## Export

```bash
python -m src.cli --export-csv giveaways.csv
```

## Refresh

Results cache for 30 minutes. To force a fetch:

```bash
python -m src.cli --force-refresh
```

## Then what

- [Configuration](./configuration.md) — the twelve environment variables
- [Architecture](./architecture.md) — how the two fetch backends differ
- [API](./api.md) — calling this from your own code
