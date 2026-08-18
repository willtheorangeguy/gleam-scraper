# Gleam.io Giveaway Scraper — Configuration

Everything is set through environment variables, read from `.env`. Start from the template:

```bash
cp .env.example .env
```

`.env` is gitignored; `.env.example` is the tracked template. Keep real values out of the
latter.

## Database

| Variable | Default | Effect |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./gleam_scraper.db` | Connection string |

Unset means SQLite in the working directory, which is the right default for local use.
PostgreSQL is for deployment — see [Deployment](./deployment.md).

## Caching and requests

| Variable | Default | Effect |
|---|---|---|
| `CACHE_TTL` | `30` | Cache lifetime, **in minutes** |
| `REQUEST_TIMEOUT` | `10` | HTTP timeout, in seconds |
| `REQUEST_DELAY_SECONDS` | `1.0` | Pause between page fetches |
| `MAX_RETRIES` | `3` | Retries for transient HTTP failures |

`REQUEST_DELAY_SECONDS` is the one to raise rather than lower. Gleam blocks access it
considers automated, and pagination means one run makes many requests — shortening the delay
is the fastest way to start collecting `403`s.

## Fetch backend

| Variable | Values | Default | Effect |
|---|---|---|---|
| `SCRAPER_MODE` | `auto`, `requests`, `browser` | `auto` | Which fetcher to use |

- **`requests`** — plain HTTP. Fast and light, and the mode Gleam most often refuses.
- **`browser`** — a real browser via Playwright. Slower, far more likely to succeed.
- **`auto`** — try HTTP, fall back to the browser on `403`.

`auto` is the sensible default: it costs nothing when HTTP works and rescues the run when it
does not. See [Architecture](./architecture.md).

## Browser backend

Only relevant when the browser fetcher runs.

| Variable | Values | Effect |
|---|---|---|
| `PLAYWRIGHT_HEADLESS` | `true` / `false` | Hide the browser window |
| `PLAYWRIGHT_BROWSER` | `chromium`, `firefox`, `webkit` | Which engine |
| `PLAYWRIGHT_WAIT_UNTIL` | `domcontentloaded`, `load`, `networkidle`, `commit` | What counts as "loaded" |
| `PLAYWRIGHT_POST_NAV_WAIT_MS` | milliseconds | Extra settle time after navigation |
| `PLAYWRIGHT_TIMEOUT_MULTIPLIER` | number | Multiplies `REQUEST_TIMEOUT` for browser navigation |

### The two that fix "browser mode returns nothing"

**`PLAYWRIGHT_WAIT_UNTIL`.** Gleam's listing is JavaScript-rendered. `domcontentloaded`
fires before the giveaways exist, so extraction finds an empty page and reports no results
rather than failing. `networkidle` waits for the fetches to finish and is the setting to try
first.

**`PLAYWRIGHT_POST_NAV_WAIT_MS`.** Even after network idle, rendering can lag. A small extra
wait is the difference between a partial list and a complete one.

`PLAYWRIGHT_TIMEOUT_MULTIPLIER` exists because a browser navigation legitimately takes far
longer than an HTTP request — reusing `REQUEST_TIMEOUT` directly would time out every time.

## Installing browser support

Playwright is optional and not installed by default:

```bash
pip install playwright
python -m playwright install chromium
```

Without it, `SCRAPER_MODE=auto` has nothing to fall back to.
