# Gleam.io Giveaway Scraper — Architecture

## Layers

```
src/
├── scraper.py      fetching and parsing        ─┐
├── database.py     models and ORM               ├─ reusable core
├── cache.py        caching layer               ─┘
├── csv_export.py   CSV output
├── ui.py           interactive terminal components  ─┐
└── cli.py          entry point                       ├─ front end
                                                     ─┘
```

The split is not incidental. `scraper.py`, `database.py`, and `cache.py` know nothing about
the terminal, which is what allows
[`gleam-scraper-web`](https://github.com/willtheorangeguy/gleam-scraper-web) to consume this
project through the API in [API](./api.md) rather than reimplementing the scraping.

Anything front-end-specific belongs in `ui.py` or `cli.py`. Adding a second front end should
require no change to the core.

## Two fetch backends

```
         SCRAPER_MODE
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 requests   auto     browser
    │         │         │
    │    try requests   │
    │         │         │
    │      403? ────────┤
    │         │         ▼
    ▼         ▼    Playwright
   HTTP    result    a real browser
```

**Gleam actively blocks automated HTTP access.** A plain request frequently returns `403`,
and no amount of header tuning reliably prevents it — the browser-like headers, retries, and
delays in `scraper.py` reduce the rate rather than eliminating it.

That is the whole reason for the second backend. `auto` tries HTTP first because it is fast
and cheap, and escalates to a real browser only when refused. Neither mode is "the right
one"; the fallback is the design.

Playwright is an **optional** dependency, so `auto` on a machine without it degrades to
`requests` alone.

## Caching

`cache.py` sits between the scraper and its callers with a TTL of `CACHE_TTL` minutes,
default 30. Results persist in the database rather than in memory, so the cache survives
restarts and is shared between the CLI and any other consumer of the API.

That is a meaningful difference from a file cache: a web front end and a terminal session hit
the same cached data, and neither triggers a re-scrape the other has already paid for.

## Storage

`database.py` uses an ORM, so SQLite and PostgreSQL are the same code path. SQLite is the
default for local use; PostgreSQL is for deployment, where multiple processes share state.

Switching is a `DATABASE_URL` change and `--init-db` — no code change.

## Pagination

Gleam paginates its listing, and the scraper walks every page automatically.

This is why `REQUEST_DELAY_SECONDS` matters more than it looks: a single run is many
requests, so a short delay compounds into a request rate that attracts blocking. Raising the
delay is usually a better response to `403`s than lowering the timeout.

## Entry point

`python -m src.cli` — the package is run as a module rather than through a console script.
