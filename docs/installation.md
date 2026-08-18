# Gleam.io Giveaway Scraper — Installation

## Requirements

| Requirement | Notes |
|---|---|
| Python 3.9+ | |
| PostgreSQL 12+ | **Optional.** SQLite is the default and is fine locally |
| Playwright | **Optional**, but needed for the browser fallback |

## Install

```bash
git clone https://github.com/willtheorangeguy/gleam-scraper.git
cd gleam-scraper

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configure

```bash
cp .env.example .env
```

Leaving `DATABASE_URL` unset gives SQLite at `gleam_scraper.db`. Everything else has a
working default — see [Configuration](./configuration.md).

## Initialise the database

```bash
python -m src.cli --init-db
```

Creates tables if absent; safe to re-run.

## Browser support

Install this **before** you need it, not after the first `403`:

```bash
pip install playwright
python -m playwright install chromium
```

Playwright is deliberately not in `requirements.txt`, which means the default install cannot
fall back to a browser. `SCRAPER_MODE=auto` on a machine without it quietly behaves like
`requests` alone — so a `403` looks like a hard failure when it is actually a missing
optional dependency.

## Verify

```bash
python -m src.cli --help
python -m src.cli
```

If the list is empty and you see `403` or `Access Denied`, that is Gleam blocking HTTP
access rather than a broken install — see [Troubleshooting](./troubleshooting.md).

## PostgreSQL

Only needed for deployment or for more than one process sharing state. Set `DATABASE_URL`
and re-run `--init-db`. See [Deployment](./deployment.md).

## Next

[Quickstart](./quickstart.md), or [Configuration](./configuration.md).
