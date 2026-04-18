"""
Web scraper for gleam.io giveaways.
"""

import logging
import os
import re
import time
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GLEAM_URL = "https://gleam.io/giveaways"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "1.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
SCRAPER_MODE = os.getenv("SCRAPER_MODE", "auto").lower()
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() in (
    "1",
    "true",
    "yes",
    "on",
)
PLAYWRIGHT_BROWSER = os.getenv("PLAYWRIGHT_BROWSER", "chromium").lower()
PLAYWRIGHT_WAIT_UNTIL = os.getenv("PLAYWRIGHT_WAIT_UNTIL", "networkidle").lower()
PLAYWRIGHT_POST_NAV_WAIT_MS = int(os.getenv("PLAYWRIGHT_POST_NAV_WAIT_MS", "750"))
PLAYWRIGHT_TIMEOUT_MULTIPLIER = int(os.getenv("PLAYWRIGHT_TIMEOUT_MULTIPLIER", "4"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    ),
)
GIVEAWAY_PATH_RE = re.compile(r"^/giveaways/[A-Za-z0-9]+$")


class GiveawayScraperError(Exception):
    """Raised for scraper failures."""


class Giveaway:
    """Represents a gleam.io giveaway."""

    def __init__(self, title: str, url: str, description: Optional[str] = None):
        self.title = title
        self.url = url
        self.description = description or ""

    def __repr__(self) -> str:
        return f"Giveaway(title={self.title!r}, url={self.url!r})"


class GleamScraper:
    """Scraper for gleam.io giveaways."""

    def __init__(
        self,
        base_url: str = GLEAM_URL,
        timeout: int = REQUEST_TIMEOUT,
        mode: str = SCRAPER_MODE,
        max_retries: int = MAX_RETRIES,
        playwright_headless: bool = PLAYWRIGHT_HEADLESS,
        playwright_browser: str = PLAYWRIGHT_BROWSER,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.mode = mode if mode in {"auto", "requests", "browser"} else "auto"
        self.max_retries = max_retries
        self.playwright_headless = playwright_headless
        self.playwright_browser = (
            playwright_browser
            if playwright_browser in {"chromium", "firefox", "webkit"}
            else "chromium"
        )
        self.session = requests.Session()
        self._session_warmed = False

        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Referer": "https://gleam.io/",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        retry = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            read=self.max_retries,
            status=self.max_retries,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def __del__(self):
        """Cleanup session."""
        if hasattr(self, "session"):
            self.session.close()

    def _build_page_url(self, page: int) -> str:
        if page <= 1:
            return self.base_url
        return f"{self.base_url}?page={page}"

    def _warm_up_session(self) -> None:
        if self._session_warmed:
            return
        self.session.get("https://gleam.io/", timeout=self.timeout)
        self._session_warmed = True

    def _get_page_with_requests(self, url: str) -> requests.Response:
        self._warm_up_session()
        response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        if response.status_code == 403:
            raise requests.HTTPError(f"403 Forbidden for {url}", response=response)
        response.raise_for_status()
        return response

    def _get_page_with_browser(self, url: str) -> str:
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise GiveawayScraperError(
                "Received 403 from direct requests and browser fallback is unavailable. "
                "Install Playwright (`pip install playwright` then "
                "`python -m playwright install chromium`) or use a reachable "
                "PostgreSQL cache populated from another environment."
            ) from exc

        try:
            with sync_playwright() as playwright:
                browser_factory = {
                    "chromium": playwright.chromium,
                    "firefox": playwright.firefox,
                    "webkit": playwright.webkit,
                }[self.playwright_browser]
                browser = browser_factory.launch(headless=self.playwright_headless)
                context = browser.new_context(user_agent=USER_AGENT, locale="en-US")
                page = context.new_page()
                wait_until = (
                    PLAYWRIGHT_WAIT_UNTIL
                    if PLAYWRIGHT_WAIT_UNTIL
                    in {"commit", "domcontentloaded", "load", "networkidle"}
                    else "networkidle"
                )
                page.goto(
                    url,
                    wait_until=wait_until,
                    timeout=self.timeout * 1000 * PLAYWRIGHT_TIMEOUT_MULTIPLIER,
                )
                if PLAYWRIGHT_POST_NAV_WAIT_MS > 0:
                    page.wait_for_timeout(PLAYWRIGHT_POST_NAV_WAIT_MS)
                content = page.content()
                context.close()
                browser.close()
                return content
        except PlaywrightTimeoutError as exc:
            raise GiveawayScraperError(
                f"Browser fallback timed out for {url}: {exc}"
            ) from exc
        except PlaywrightError as exc:
            if "Executable doesn't exist" in str(exc):
                raise GiveawayScraperError(
                    "Playwright browser binary is not installed. "
                    "Run `python -m playwright install chromium`."
                ) from exc
            raise GiveawayScraperError(
                f"Browser fallback failed for {url}: {exc}"
            ) from exc

    def _get_page(self, page: int = 1) -> BeautifulSoup:
        """Fetch and parse a page of giveaways."""
        url = self._build_page_url(page)
        logger.info("Fetching page %s: %s", page, url)

        if self.mode in {"auto", "requests"}:
            try:
                response = self._get_page_with_requests(url)
                soup = BeautifulSoup(response.content, "html.parser")
                if self._is_blocked_page(soup):
                    if self.mode == "auto":
                        logger.warning(
                            "Request mode returned a blocked page for %s. "
                            "Trying browser fallback mode.",
                            url,
                        )
                    else:
                        raise GiveawayScraperError(
                            "Gleam returned a blocked page in requests mode."
                        )
                else:
                    return soup
            except requests.HTTPError as exc:
                status_code = (
                    exc.response.status_code if exc.response is not None else None
                )
                if status_code == 403 and self.mode == "auto":
                    logger.warning(
                        "Received HTTP 403 for %s. Trying browser fallback mode.", url
                    )
                else:
                    raise GiveawayScraperError(
                        f"Failed to fetch page {page}: {exc}"
                    ) from exc
            except requests.RequestException as exc:
                if self.mode == "requests":
                    raise GiveawayScraperError(
                        f"Failed to fetch page {page}: {exc}"
                    ) from exc
                logger.warning(
                    "Request mode failed for %s (%s). Trying browser fallback.",
                    url,
                    exc,
                )

        html = self._get_page_with_browser(url)
        soup = BeautifulSoup(html, "html.parser")
        if self._is_blocked_page(soup):
            raise GiveawayScraperError(
                "Gleam is still returning a blocked page. "
                "This endpoint may require interactive access or additional permissions."
            )
        return soup

    def _is_blocked_page(self, soup: BeautifulSoup) -> bool:
        if self._has_giveaway_content(soup):
            return False

        title = soup.title.get_text(" ", strip=True).lower() if soup.title else ""
        text = soup.get_text(" ", strip=True).lower()
        title_markers = (
            "access denied",
            "attention required",
            "forbidden",
            "just a moment",
        )
        body_markers = (
            "access denied",
            "verify you are human",
            "captcha",
            "unusual traffic",
            "cf-ray",
        )
        if any(marker in title for marker in title_markers):
            return True
        return any(marker in text for marker in body_markers)

    def _has_giveaway_content(self, soup: BeautifulSoup) -> bool:
        if soup.select("a.preview-tile__campaign-link[href]"):
            return True
        if soup.select("a.giveaway-card[href]"):
            return True

        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            if GIVEAWAY_PATH_RE.match(href):
                return True
        return False

    def _extract_giveaways_from_page(
        self, soup: BeautifulSoup
    ) -> tuple[List[Giveaway], bool]:
        """Extract giveaways from a parsed page. Returns (giveaways, has_more_pages)."""
        giveaways: List[Giveaway] = []
        seen_urls = set()

        preview_links = soup.select("a.preview-tile__campaign-link[href]")
        if preview_links:
            for link in preview_links:
                href = link.get("href", "").strip()
                if not GIVEAWAY_PATH_RE.match(href):
                    continue

                url = urljoin(self.base_url, href)
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title_elem = link.select_one(".preview-tile__title")
                title = title_elem.get_text(strip=True) if title_elem else ""
                if not title:
                    title = link.get_text(" ", strip=True)
                if not title:
                    continue

                tile_root = link.parent
                while tile_root is not None and tile_root.name != "[document]":
                    classes = tile_root.get("class", [])
                    if "preview-tile__root" in classes:
                        break
                    tile_root = tile_root.parent

                description = ""
                if tile_root is not None and tile_root.name != "[document]":
                    desc_elem = tile_root.select_one(".preview-tile__bottom-panel")
                    if desc_elem:
                        description = desc_elem.get_text(" ", strip=True)

                giveaways.append(Giveaway(title, url, description))

            return giveaways, False

        containers = soup.find_all("a", class_="giveaway-card")
        if not containers:
            containers = soup.find_all("div", class_=lambda x: x and "giveaway" in x)

        for container in containers:
            title_elem = container.find("h2") or container.find("h3")
            if not title_elem:
                title_elem = container.find(class_="title")
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            if not title:
                continue

            url_elem = (
                container.find("a", href=True) if container.name != "a" else container
            )
            if not url_elem:
                continue
            url = url_elem.get("href", "").strip()
            if not url:
                continue
            url = urljoin(self.base_url, url)
            if url in seen_urls:
                continue
            seen_urls.add(url)

            desc_elem = container.find(class_="description") or container.find("p")
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            giveaways.append(Giveaway(title, url, description))

        next_button = soup.select_one("a[rel='next'], a.next, .pagination-next a")
        has_more = bool(next_button and next_button.get("href"))
        return giveaways, has_more

    def scrape_all_giveaways(self) -> List[Giveaway]:
        """Scrape all giveaways from all pages."""
        all_giveaways: List[Giveaway] = []
        page = 1
        max_pages = 100

        try:
            while page <= max_pages:
                logger.info("Scraping page %s...", page)
                soup = self._get_page(page)
                giveaways, has_more = self._extract_giveaways_from_page(soup)

                if not giveaways:
                    logger.info("No giveaways found on page %s, stopping", page)
                    break

                all_giveaways.extend(giveaways)
                logger.info("Found %s giveaways on page %s", len(giveaways), page)

                if not has_more:
                    logger.info("No more pages to scrape")
                    break

                page += 1
                time.sleep(REQUEST_DELAY_SECONDS)

        except GiveawayScraperError as exc:
            logger.error("Scraping failed: %s", exc)
            if not all_giveaways:
                raise

        logger.info("Total giveaways scraped: %s", len(all_giveaways))
        return all_giveaways
