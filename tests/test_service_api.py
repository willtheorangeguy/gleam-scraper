"""
Tests for the public service API.
"""

import pytest

from gleam_scraper import service
from src.scraper import Giveaway


class FakeDBSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeCacheManager:
    def __init__(self, db):
        self.db = db

    def get_giveaways(
        self, force_refresh=False, scraper_mode=None, playwright_headless=None
    ):
        if force_refresh:
            return [Giveaway("Fresh Giveaway", "https://gleam.io/giveaways/FRESH1", "")]
        return [Giveaway("Cached Giveaway", "https://gleam.io/giveaways/CACHED1", "Test")]


def test_list_competitions_maps_results_and_closes_session(monkeypatch):
    fake_db = FakeDBSession()

    monkeypatch.setattr(service, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(service, "CacheManager", FakeCacheManager)

    competitions = service.list_competitions()

    assert len(competitions) == 1
    assert competitions[0].title == "Cached Giveaway"
    assert competitions[0].url == "https://gleam.io/giveaways/CACHED1"
    assert competitions[0].description == "Test"
    assert fake_db.closed


def test_list_competitions_rejects_invalid_mode():
    with pytest.raises(ValueError):
        service.list_competitions(scraper_mode="invalid-mode")


def test_refresh_competitions_sets_force_refresh(monkeypatch):
    fake_db = FakeDBSession()

    monkeypatch.setattr(service, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(service, "CacheManager", FakeCacheManager)

    competitions = service.refresh_competitions()

    assert len(competitions) == 1
    assert competitions[0].title == "Fresh Giveaway"
    assert fake_db.closed


def test_competitions_to_dicts():
    competitions = [
        service.Competition(
            title="Title",
            url="https://gleam.io/giveaways/AAA11",
            description="Description",
        )
    ]

    payload = service.competitions_to_dicts(competitions)

    assert payload == [
        {
            "title": "Title",
            "url": "https://gleam.io/giveaways/AAA11",
            "description": "Description",
        }
    ]

