# Gleam.io Giveaway Scraper — Roadmap

Known gaps, observed from the code. Limitations, not a schedule.

## Documentation drift already corrected here

The README described Docker as **"Docker Usage (Future)"**, but `docker-compose.yml` defines
a working PostgreSQL 15 service with a health check and volume, plus an app service. The
capability shipped; the documentation did not catch up. [Deployment](./deployment.md) now
documents it as present.

## Security

**The compose file ships default credentials** — `gleam_user` and `gleam_password` — in a
public repository, and publishes port `5432` to the host. Fine for local development, not for
anything reachable. They should be overridable from the environment rather than requiring the
file to be edited, and the port mapping should probably not be the default.

## Gaps

**No automatic scheduling.** Refreshing is manual or externally scheduled. Since refreshing on
a request path would get a deployment blocked, a built-in scheduler with a sane default
interval would make the web use case safer by construction rather than by documentation.

**No signal that the browser fallback is unavailable.** `SCRAPER_MODE=auto` on a machine
without Playwright behaves like `requests` alone. The user sees a `403` and no indication that
an optional dependency would have rescued it — a one-line warning would save the whole
diagnostic path.

**Blocking is not distinguishable from emptiness in browser mode.** A `403` is explicit, but a
browser run that loads before rendering returns zero giveaways and looks identical to a
genuinely empty listing.

**Toolchain differs from its siblings.** This project uses Black and Flake8 where the rest of
the org uses Ruff. Not wrong, but it means contributors carry the wrong muscle memory.

**No console script.** Invocation is `python -m src.cli` rather than a named command, and the
package is not installable as one.

## Inherent limitations

**Gleam actively blocks automation.** The two-backend design works with that rather than
solving it; server-side controls can still refuse a browser session, and nothing in this
project changes that.

**Scraped output is unversioned.** A Gleam layout change breaks parsing with no warning.

## Non-goals

- **Entering giveaways.** This lists and opens them; entry is manual, deliberately.
- **Evading blocks.** The browser fallback exists to fetch a page the way a person would, not
  to defeat controls.
- **Being the web front end.** That is
  [gleam-scraper-web](https://github.com/willtheorangeguy/gleam-scraper-web), which consumes
  the API in [API](./api.md).
