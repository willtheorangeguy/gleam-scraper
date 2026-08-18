# Gleam.io Giveaway Scraper — Deployment

## Docker Compose

`docker-compose.yml` defines two services: a PostgreSQL 15 database with a health check and a
persistent volume, and the application.

```bash
docker compose up -d
docker compose logs -f app
docker compose down
```

## Change the default credentials

The compose file ships with:

```yaml
POSTGRES_USER: gleam_user
POSTGRES_PASSWORD: gleam_password
POSTGRES_DB: gleam_scraper
```

These are **development defaults published in a public repository**. Override them before
running this anywhere reachable, and set a matching `DATABASE_URL` in your environment rather
than editing the file:

```bash
POSTGRES_PASSWORD=... docker compose up -d
```

The compose file also publishes port `5432` to the host. Remove that mapping unless you
genuinely need to reach the database from outside the compose network.

## Standalone image

```bash
docker build -t gleam-scraper .
docker run --env-file .env gleam-scraper
```

Pass configuration through `--env-file` rather than baking it into the image.

## PostgreSQL rather than SQLite

SQLite is the local default and is fine for one process. Use PostgreSQL when:

- More than one process reads or writes — a web front end alongside a scheduled scrape.
- You want the cache to survive container replacement.

Switching is a `DATABASE_URL` change plus `--init-db`. The ORM means no code changes.

## Initialising

```bash
docker compose run --rm app python -m src.cli --init-db
```

Safe to run repeatedly; it creates tables only if they are absent.

## Scheduling refreshes

Do **not** refresh on a request path. A full run walks every page of Gleam's listing, and
doing that per visitor will get the deployment blocked.

Run it on a schedule instead, and let everything else read through the cache:

```bash
docker compose run --rm app python -m src.cli --force-refresh
```

`CACHE_TTL` should be at least as long as the gap between scheduled runs, so reads never fall
through to an unscheduled scrape. See [API](./api.md).

## Browser support in a container

The browser fallback needs Playwright and its browser inside the image. If `403`s appear in
deployment but not locally, confirm the image actually has them — otherwise `SCRAPER_MODE=auto`
silently has nothing to fall back to. See [Troubleshooting](./troubleshooting.md).
