# Gleam.io Giveaway Scraper — Troubleshooting

## 403 or Access Denied

The most common outcome, and expected rather than exceptional — Gleam blocks automated HTTP
access.

1. **Confirm browser support is installed.** Without it, `auto` has nothing to fall back to:

   ```bash
   pip install playwright
   python -m playwright install chromium
   ```

2. **Force browser mode:**

   ```bash
   python -m src.cli --force-refresh --scraper-mode browser
   ```

3. **Watch it:**

   ```bash
   python -m src.cli --force-refresh --scraper-mode browser --headed
   ```

4. **Slow down.** Raise `REQUEST_DELAY_SECONDS`. Pagination means one run is many requests,
   and a short delay is what attracts blocking in the first place.

If browser mode is also refused, server-side controls are rejecting your environment and no
setting here will change that.

## Browser mode runs but returns no giveaways

The page loaded before the content rendered. Gleam's listing is JavaScript-driven, so
"loaded" and "populated" are different moments:

```bash
PLAYWRIGHT_WAIT_UNTIL=networkidle
PLAYWRIGHT_POST_NAV_WAIT_MS=2000
```

`networkidle` waits for the fetches to settle; the extra wait covers rendering lag. A partial
list usually means the wait is close but short.

## Browser mode times out

Browser navigation legitimately takes far longer than an HTTP request. Raise
`PLAYWRIGHT_TIMEOUT_MULTIPLIER` rather than `REQUEST_TIMEOUT` — the multiplier exists so the
two can differ.

## Results are stale

Cached for `CACHE_TTL` minutes, 30 by default:

```bash
python -m src.cli --force-refresh
```

Remember the cache lives in the database and is shared, so another consumer may have
populated it.

## Database errors on first run

Initialise the schema:

```bash
python -m src.cli --init-db
```

Safe to re-run. After changing `DATABASE_URL` to a different database, run it again — the new
database has no tables.

## "no such table" after switching to PostgreSQL

Same cause. `--init-db` creates tables in whichever database `DATABASE_URL` points at, and
switching does not migrate anything.

## Works locally, 403 in Docker

Almost always missing browser support inside the image. `SCRAPER_MODE=auto` degrades silently
to `requests` when Playwright is absent, so the container behaves differently from your
machine with no error explaining why. See [Deployment](./deployment.md).

## Everything is slow

Check whether you are refreshing on every run. `--force-refresh` walks every page of the
listing with `REQUEST_DELAY_SECONDS` between fetches. Normal use should read through the
cache and refresh on a schedule.

## Interactive list will not scroll or exit

Arrow keys navigate, `Enter` selects, `Esc` leaves dialogs and quits from the main list. The
interface needs a terminal capable of raw key input — piping or running it under a
non-interactive shell will not work.
