# Known Issues — gleam-scraper

Concrete defects and gaps found while writing this repository's documentation in
August 2026. **Nothing here was changed** — each one needs a code, configuration, or
licensing decision rather than a documentation one.

Ordered by severity. See [`docs/roadmap.md`](../roadmap.md) for the narrative version,
which also covers deliberate non-goals.


**4 open:** 2 medium, 2 low.

## 1. Compose ships default credentials and publishes PostgreSQL

**Severity:** Medium  
**Where:** `docker-compose.yml`

**What:** `gleam_user` / `gleam_password` are hardcoded in a public repository, and port `5432` is mapped to the host.

**Why it matters:** Fine locally, not for anything reachable. Nothing in the app needs the port published.

**Suggested fix:** Take credentials from the environment, and drop or loopback-bind the port mapping.

## 2. SCRAPER_MODE=auto degrades silently without Playwright

**Severity:** Medium  
**Where:** `src/scraper.py`

**What:** Playwright is an optional dependency. Without it, `auto` behaves like `requests` alone.

**Why it matters:** The user sees a `403` — the expected symptom of Gleam blocking — with no indication that an optional install would have rescued it. This is also the usual cause of "works locally, 403 in Docker".

**Suggested fix:** Warn once when `auto` cannot fall back.

## 3. Blocking is indistinguishable from emptiness in browser mode

**Severity:** Low  
**Where:** `src/scraper.py`

**What:** A `403` is explicit, but a browser run that loads before the JavaScript renders returns zero giveaways — identical to a genuinely empty listing.

**Why it matters:** Users cannot tell which happened.

**Suggested fix:** Distinguish "page loaded but no items found" from "no items exist".

## 4. Toolchain differs from the rest of the org

**Severity:** Low  
**Where:** `requirements.txt`, CI

**What:** This project uses Black and Flake8 where the other repositories use Ruff.

**Why it matters:** Contributors arrive with the wrong muscle memory.

**Suggested fix:** Either adopt Ruff or note the difference in CONTRIBUTING.


---

## Also, across every repository

**`.bandit` is present on disk but untracked in git.** Verified in PyWorkout, treklogger,
skyscanner-cli, booking-cli, piggy, and aibot — the config file exists locally in each but
`git ls-files` does not know about it, so none of it reached GitHub.

The August 2026 security sweep therefore looks complete locally and landed nowhere. Worth
checking across all 44 repositories it covered.
