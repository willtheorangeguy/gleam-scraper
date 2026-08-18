# Gleam.io Giveaway Scraper — FAQ

## Why do I get 403 Access Denied?

Because Gleam blocks automated HTTP access. This is the normal starting point, not a broken
install. The browser-like headers, retries, and delays in the scraper reduce how often it
happens; they do not prevent it.

Install browser support and let the fallback do its job:

```bash
pip install playwright
python -m playwright install chromium
python -m src.cli --force-refresh --scraper-mode browser
```

## Why is Playwright not installed already?

It is deliberately optional — a browser download is a heavy dependency for people whose
network is not being blocked. The consequence to know about: on a machine without it,
`SCRAPER_MODE=auto` has nothing to fall back to and behaves like `requests` alone, so a
`403` looks like a hard failure.

## SQLite or PostgreSQL?

SQLite unless more than one process needs the data. It is the default, needs no setup, and is
fine for a single terminal user.

PostgreSQL is for deployment — a web front end alongside a scheduled scrape, or state that
must survive container replacement. Switching is a `DATABASE_URL` change plus `--init-db`,
with no code change.

## Why are results the same as ten minutes ago?

They are cached, for `CACHE_TTL` minutes — 30 by default. Force a fetch:

```bash
python -m src.cli --force-refresh
```

## Where is the cache stored?

In the database, not in memory or a file. That means it survives restarts and is **shared**
between the CLI and anything using the Python API, so neither pays for a scrape the other has
already done.

## Can I use this from my own code?

Yes — that is what the Python API is for.
[gleam-scraper-web](https://github.com/willtheorangeguy/gleam-scraper-web) is built on it.
Call `list_competitions`, not `refresh_competitions`, from anything user-facing. See
[API](./api.md).

## Browser mode runs but finds nothing.

Gleam's listing is JavaScript-rendered, so the browser can finish loading before the
giveaways exist. Set `PLAYWRIGHT_WAIT_UNTIL=networkidle`, and add
`PLAYWRIGHT_POST_NAV_WAIT_MS` if the list is still partial. See
[Configuration](./configuration.md).

## Should I lower REQUEST_DELAY_SECONDS to speed things up?

No — raise it if anything. Pagination means one run is many requests, so a short delay
compounds into a rate that attracts blocking. Speed here is bought with `403`s.

## Is the Docker setup usable?

Yes. The README previously called it "future", but `docker-compose.yml` defines a working
PostgreSQL service and an app service. **Change the default credentials before exposing it** —
see [Deployment](./deployment.md).

## Does this enter giveaways for me?

No. It scrapes listings and opens them in your browser. Entering is manual.
