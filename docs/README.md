# Gleam.io Giveaway Scraper — Documentation

A terminal tool that scrapes gleam.io, caches results in a database, and lets you browse
them interactively. Its structure is deliberately front-end-agnostic — the scraper, database,
and cache layers are consumed by a separate web application through a documented Python API.

```
gleam-scraper/
├── docs/
│   ├── README.md          this page
│   ├── quickstart.md      install and browse in five minutes
│   ├── installation.md    prerequisites, database setup, browser support
│   ├── configuration.md   every environment variable
│   ├── architecture.md    the two fetch backends and the reusable core
│   ├── api.md             the stable Python API for front ends
│   ├── deployment.md      Docker and PostgreSQL
│   ├── development.md     tests, formatting, linting
│   ├── faq.md             403s, SQLite vs PostgreSQL, cache staleness
│   ├── troubleshooting.md access denied, empty results, database errors
│   └── roadmap.md         known gaps and non-goals
└── src/
    ├── scraper.py         fetching and parsing — reusable
    ├── database.py        models and ORM — reusable
    ├── cache.py           caching layer — reusable
    ├── csv_export.py      CSV output
    ├── ui.py              interactive terminal components
    └── cli.py             entry point
```

## Pages

- [Quickstart](./quickstart.md) — install, initialise, browse
- [Installation](./installation.md) — Python, database, optional browser support
- [Configuration](./configuration.md) — all twelve environment variables
- [Architecture](./architecture.md) — why there are two fetch backends, and the reusable core
- [API](./api.md) — the stable functions a web front end should call
- [Deployment](./deployment.md) — Docker Compose with PostgreSQL
- [Development](./development.md) — tests, coverage, formatting, linting
- [FAQ](./faq.md) — 403s, database choice, cache behaviour
- [Troubleshooting](./troubleshooting.md) — access denied, no results, database problems
- [Roadmap](./roadmap.md) — known gaps and non-goals

## The thing to know first

**Gleam actively blocks automated access.** A plain HTTP request frequently returns `403`.
That is why there are two fetch backends and why `SCRAPER_MODE=auto` falls back to a real
browser — see [Architecture](./architecture.md). If you are getting `403`, that is the
expected starting point, not a misconfiguration.

## Related

[`gleam-scraper-web`](https://github.com/willtheorangeguy/gleam-scraper-web) is the web front
end. It consumes the API in [API](./api.md) rather than reimplementing any of this.
