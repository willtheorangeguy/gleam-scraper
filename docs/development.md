# Gleam.io Giveaway Scraper — Development

## Setup

```bash
pip install -r requirements.txt
pip install playwright && python -m playwright install chromium   # for browser-mode work
cp .env.example .env
python -m src.cli --init-db
```

## Tests

```bash
pytest -v
pytest --cov=src tests/
```

## Formatting and linting

```bash
black src/ tests/
flake8 src/ tests/
```

Note this project uses **Black and Flake8**, not Ruff — unlike most of the sibling repos in
this org. Running `ruff` here will not match what the project expects.

## Where to make changes

| Change | Where | Note |
|---|---|---|
| Parsing or fetching | `src/scraper.py` | Keep it front-end agnostic |
| Models or schema | `src/database.py` | Re-run `--init-db` |
| Cache behaviour | `src/cache.py` | Shared with every consumer |
| CSV columns | `src/csv_export.py` | |
| Terminal interaction | `src/ui.py` | |
| Flags and entry point | `src/cli.py` | |

## Keep the core reusable

`scraper.py`, `database.py`, and `cache.py` must not import from `ui.py` or `cli.py`. That
boundary is what lets
[`gleam-scraper-web`](https://github.com/willtheorangeguy/gleam-scraper-web) use this project
as a library through the API in [API](./api.md).

A terminal-specific concern leaking into the core breaks that consumer without breaking the
CLI, so it will not be caught by running the tool.

## The public API is a contract

`init_database`, `list_competitions`, `refresh_competitions`, and `competitions_to_dicts` are
consumed by a separate repository. Changing their signatures or return shapes breaks it
silently from this side.

## Testing against a blocked site

Gleam returns `403` to plain HTTP often enough that a failing scrape during development is
usually the site, not the change. Confirm with:

```bash
python -m src.cli --force-refresh --scraper-mode browser --headed
```

Watching the browser is faster than reasoning about the response.
