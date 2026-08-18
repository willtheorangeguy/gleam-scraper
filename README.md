<!-- Logo -->
<h1 align="center">Gleam.io Giveaway Scraper</h1>

<!-- Copy -->
<h4 align="center">Scrape, cache, and interactively browse gleam.io giveaways from the terminal, with CSV export and a stable Python API.</h4>

<!-- Badges -->
<div align="center">
  <img alt="GitHub Issues" src="https://img.shields.io/github/issues/willtheorangeguy/gleam-scraper">
  <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/gleam-scraper">
  <img alt="License" src="https://img.shields.io/github/license/willtheorangeguy/gleam-scraper">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-blue">
</div>

<!-- Navigation -->
<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support">Support</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features

- Scrapes every giveaway with automatic pagination.
- Two fetch backends — plain HTTP requests, or a real browser — with automatic fallback when Gleam blocks the simpler one.
- Persistent cache in SQLite locally or PostgreSQL in production, with a 30-minute refresh.
- Interactive terminal list with arrow-key navigation and one-key browser opening.
- CSV export.
- A stable Python API, so a web front end can consume it without reimplementing the scraper.

## Installation

```bash
git clone https://github.com/willtheorangeguy/gleam-scraper.git
cd gleam-scraper
pip install -r requirements.txt
cp .env.example .env
python -m src.cli --init-db
```

Requires Python 3.9+. SQLite is the default; PostgreSQL is optional. See [`docs/installation.md`](docs/installation.md).

## Usage

```bash
python -m src.cli
```

Arrow keys to navigate, `Enter` to act on a giveaway, `Esc` to quit.

## Documentation

Full documentation lives in [`docs/`](docs/README.md):
[Quickstart](docs/quickstart.md) · [Installation](docs/installation.md) · [Configuration](docs/configuration.md) · [Architecture](docs/architecture.md) · [API](docs/api.md) · [Deployment](docs/deployment.md) · [FAQ](docs/faq.md) · [Troubleshooting](docs/troubleshooting.md) · [Roadmap](docs/roadmap.md)

## Support

Open a [GitHub Discussion](https://github.com/willtheorangeguy/gleam-scraper/discussions/new) or file an [issue](https://github.com/willtheorangeguy/gleam-scraper/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## Credits

Built with [Playwright](https://playwright.dev/python/), [SQLAlchemy](https://www.sqlalchemy.org/), and [PostgreSQL](https://www.postgresql.org/).

## License

MIT — see [`LICENSE.md`](LICENSE.md).

> For personal use. Gleam actively blocks automated access, and the browser fallback exists to work with that rather than around it — keep request rates reasonable.
