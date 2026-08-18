# Gleam.io Giveaway Scraper — Python API

This project exposes no HTTP API. It exposes a **stable Python package API**, so a separate
front end can use the scraper as a library instead of reimplementing it.

[`gleam-scraper-web`](https://github.com/willtheorangeguy/gleam-scraper-web) is the intended
consumer.

```python
from gleam_scraper import init_database, list_competitions, competitions_to_dicts

init_database()
competitions = list_competitions(force_refresh=False, scraper_mode="auto")
payload = competitions_to_dicts(competitions)
```

## Functions

| Function | Purpose |
|---|---|
| `init_database()` | Create tables if they do not exist. Safe to call on every start |
| `list_competitions(force_refresh=False, scraper_mode="auto")` | Cached read; scrapes only when the cache is cold or `force_refresh=True` |
| `refresh_competitions(...)` | Force a scrape regardless of cache state |
| `competitions_to_dicts(...)` | Convert ORM objects into plain dictionaries, ready to serialise |

## Which one to call

**`list_competitions` for anything user-facing.** It respects the cache, so a page load
costs nothing when the data is fresh and does not trigger a scrape per visitor.

**`refresh_competitions` only from a deliberate action** — a scheduled job, or an explicit
refresh button. Calling it on a request path means every visitor triggers a full paginated
scrape, which is the fastest way to get the deployment blocked by Gleam.

## `competitions_to_dicts` exists for a reason

`list_competitions` returns ORM objects bound to a session. Serialising those directly
couples your front end to the database layer and breaks once the session closes.
`competitions_to_dicts` is the boundary — convert, then hand the plain data to your template
or JSON response.

## The cache is shared

Caching lives in the database, not in the process. A web front end and a terminal session
consult the same cached rows, so neither pays for a scrape the other has already done. See
[Architecture](./architecture.md).

## Configuration is shared too

The API reads the same environment variables as the CLI — `DATABASE_URL`, `CACHE_TTL`,
`SCRAPER_MODE`, and the Playwright settings. A consumer configures behaviour through its own
environment rather than through function arguments. See [Configuration](./configuration.md).

The exception is `scraper_mode`, which can be passed per call to override the environment for
one operation.

## Stability

These four functions are the supported surface. Everything else in `src/` is internal and may
change — a front end importing `src.scraper` directly is reaching past the boundary this API
exists to provide.
