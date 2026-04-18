"""
Tests for scraper module
"""

import pytest
import requests
from bs4 import BeautifulSoup
from src.scraper import Giveaway, GleamScraper, GiveawayScraperError


def test_giveaway_creation():
    """Test creating a Giveaway object"""
    giveaway = Giveaway("Test Giveaway", "https://gleam.io/test", "Test Description")
    assert giveaway.title == "Test Giveaway"
    assert giveaway.url == "https://gleam.io/test"
    assert giveaway.description == "Test Description"


def test_giveaway_repr():
    """Test Giveaway string representation"""
    giveaway = Giveaway("Test", "https://gleam.io/test")
    assert "Test" in repr(giveaway)
    assert "https://gleam.io/test" in repr(giveaway)


def test_giveaway_empty_description():
    """Test Giveaway with empty description"""
    giveaway = Giveaway("Test", "https://gleam.io/test")
    assert giveaway.description == ""


def test_scraper_init():
    """Test GleamScraper initialization"""
    scraper = GleamScraper()
    assert scraper.base_url == "https://gleam.io/giveaways"
    assert scraper.timeout > 0
    scraper.__del__()


def test_scraper_custom_url():
    """Test GleamScraper with custom URL"""
    custom_url = "https://example.com/giveaways"
    scraper = GleamScraper(base_url=custom_url)
    assert scraper.base_url == custom_url
    scraper.__del__()


def test_scraper_headed_mode_can_be_forced():
    """Test Playwright headless mode can be overridden."""
    scraper = GleamScraper(mode="browser", playwright_headless=False)
    assert scraper.playwright_headless is False
    scraper.__del__()


def test_scraper_sets_browser_like_headers():
    """Test scraper default headers are browser-like"""
    scraper = GleamScraper()
    assert "User-Agent" in scraper.session.headers
    assert "Accept" in scraper.session.headers
    assert "Accept-Language" in scraper.session.headers
    scraper.__del__()


def test_get_page_falls_back_to_browser_on_403(monkeypatch):
    """Test auto mode falls back to browser mode after a 403."""
    scraper = GleamScraper(mode="auto")

    def fake_requests_fetch(_url: str):
        response = requests.Response()
        response.status_code = 403
        raise requests.HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr(scraper, "_get_page_with_requests", fake_requests_fetch)
    monkeypatch.setattr(scraper, "_get_page_with_browser", lambda _url: "<html></html>")

    soup = scraper._get_page(1)
    assert soup is not None
    scraper.__del__()


def test_get_page_requests_mode_raises_on_403(monkeypatch):
    """Test requests-only mode surfaces a scraper error on 403."""
    scraper = GleamScraper(mode="requests")

    def fake_requests_fetch(_url: str):
        response = requests.Response()
        response.status_code = 403
        raise requests.HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr(scraper, "_get_page_with_requests", fake_requests_fetch)

    with pytest.raises(GiveawayScraperError):
        scraper._get_page(1)

    scraper.__del__()


def test_get_page_browser_mode_uses_browser_fetch(monkeypatch):
    """Test browser mode fetches through browser path directly."""
    scraper = GleamScraper(mode="browser")

    monkeypatch.setattr(scraper, "_get_page_with_browser", lambda _url: "<html></html>")
    monkeypatch.setattr(
        scraper,
        "_get_page_with_requests",
        lambda _url: (_ for _ in ()).throw(
            AssertionError("requests mode should not run")
        ),
    )

    soup = scraper._get_page(1)
    assert soup is not None
    scraper.__del__()


def test_blocked_page_detection():
    """Test blocked-page detection on Access Denied content."""
    scraper = GleamScraper()
    blocked_html = (
        "<html><head><title>Access Denied</title></head><body>forbidden</body></html>"
    )

    assert scraper._is_blocked_page(BeautifulSoup(blocked_html, "html.parser"))
    scraper.__del__()


def test_blocked_page_detection_ignores_valid_giveaway_dom():
    """Valid giveaway DOM should not be classified as blocked."""
    scraper = GleamScraper()
    valid_html = """
    <html>
      <head><title>Free Giveaways & Sweepstakes | Win Prizes with Gleam</title></head>
      <body>
        <div class="preview-tile__root">
          <a class="preview-tile__campaign-link" href="/giveaways/ABC12">
            <p class="preview-tile__title">Test Giveaway</p>
          </a>
          <a class="preview-tile__brand-link" href="/giveaways/by/test">
            <p class="preview-tile__bottom-panel">1 day left · by Test</p>
          </a>
        </div>
      </body>
    </html>
    """

    assert not scraper._is_blocked_page(BeautifulSoup(valid_html, "html.parser"))
    scraper.__del__()


def test_extract_preview_tile_giveaways_with_dedup():
    """Extract giveaways from current preview-tile markup and dedupe duplicates."""
    scraper = GleamScraper()
    html = """
    <html><body>
      <div class="preview-tile__root">
        <a class="preview-tile__campaign-link" href="/giveaways/AAA11">
          <p class="preview-tile__title">First Giveaway</p>
        </a>
        <a class="preview-tile__campaign-link" href="/giveaways/AAA11">
          2 days left · by Someone
        </a>
        <a class="preview-tile__brand-link" href="/giveaways/by/someone">
          <p class="preview-tile__bottom-panel">2 days left · by Someone</p>
        </a>
      </div>
      <div class="preview-tile__root">
        <a class="preview-tile__campaign-link" href="/giveaways/BBB22">
          <p class="preview-tile__title">Second Giveaway</p>
        </a>
        <a class="preview-tile__brand-link" href="/giveaways/by/other">
          <p class="preview-tile__bottom-panel">5 days left · by Other</p>
        </a>
      </div>
    </body></html>
    """

    giveaways, has_more = scraper._extract_giveaways_from_page(
        BeautifulSoup(html, "html.parser")
    )

    assert len(giveaways) == 2
    assert giveaways[0].title == "First Giveaway"
    assert giveaways[0].url.endswith("/giveaways/AAA11")
    assert "2 days left" in giveaways[0].description
    assert giveaways[1].title == "Second Giveaway"
    assert not has_more
    scraper.__del__()
