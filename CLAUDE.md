# CLAUDE.md

## Project Overview

Gleam.io Giveaway Scraper — a Python CLI tool that scrapes, caches, and interactively browses gleam.io giveaways. Features persistent caching (SQLite/PostgreSQL), interactive TUI navigation, CSV export, and Docker support. Published to PyPI.

## Architecture

```
src/              # Core application modules
  cli.py          # Click/Typer CLI entry point
  scraper.py      # Web scraping (requests + Playwright fallback)
  database.py     # SQLAlchemy models (Giveaway, ScraperMetadata)
  cache.py        # Cache layer with configurable TTL
  ui.py           # TUI interface (prompt-toolkit + rich)
  csv_export.py   # CSV export

gleam_scraper/    # Public API package for external consumers
  service.py      # Stable service layer

tests/            # pytest test suite (in-memory SQLite)
```

## Commands

### Run
```bash
python -m src.cli                # Interactive mode
python -m src.cli --help         # All options
```

### Test
```bash
pytest -v                        # Run all tests
pytest --cov=src tests/          # With coverage
```

### Lint & Format
```bash
ruff check .                     # Lint (used in CI)
black src/ tests/                # Format (88 char line-length)
mypy                             # Type check
```

### Build
```bash
python -m build                  # Creates wheel + sdist in dist/
```

### Docker
```bash
docker-compose up                # App + PostgreSQL
```

## CI Pipeline

GitHub Actions runs on push to main and PRs:
1. **Lint**: `ruff check .`
2. **Test**: `pytest` across Python 3.10, 3.11, 3.12
3. **Build**: Creates distributable packages

Releases publish to PyPI via OIDC on GitHub Release events.

## Code Conventions

- **Formatter**: Black, 88-char lines, target Python 3.9+
- **Linter**: Ruff (CI), flake8 (optional)
- **Type hints**: Partial coverage; mypy configured but `disallow_untyped_defs = false`
- **Naming**: PascalCase classes, snake_case functions, UPPER_SNAKE_CASE constants, `_leading_underscore` for private methods
- **Minimum Python**: 3.9

## Key Design Patterns

- Scraper uses requests with automatic fallback to Playwright on 403/block pages
- Retry logic with exponential backoff for HTTP requests
- Cache TTL defaults to 30 minutes (configurable via `CACHE_TTL` env var)
- Database abstraction supports SQLite (dev) and PostgreSQL (prod) via `DATABASE_URL`

## Environment Variables

See `.env.example` for all options. Key ones:
- `DATABASE_URL` — database connection string (default: SQLite)
- `CACHE_TTL` — cache duration in minutes
- `SCRAPER_MODE` — auto/requests/browser
