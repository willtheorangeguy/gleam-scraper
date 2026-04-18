"""
Tests for cache module
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, Giveaway as GiveawayModel, ScraperMetadata
from src.cache import CacheManager
from src.scraper import Giveaway


@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_cache_invalid_when_empty(test_db):
    """Test that cache is invalid when empty"""
    cache_manager = CacheManager(test_db, cache_ttl_minutes=30)
    assert not cache_manager.is_cache_valid()


def test_cache_valid_when_recent(test_db):
    """Test that cache is valid when recent"""
    # Add recent metadata
    metadata = ScraperMetadata(
        last_successful_scrape=datetime.utcnow(),
        last_scrape_count=5,
    )
    test_db.add(metadata)
    test_db.commit()

    cache_manager = CacheManager(test_db, cache_ttl_minutes=30)
    assert cache_manager.is_cache_valid()


def test_cache_invalid_when_stale(test_db):
    """Test that cache is invalid when stale"""
    # Add old metadata
    metadata = ScraperMetadata(
        last_successful_scrape=datetime.utcnow() - timedelta(hours=1),
        last_scrape_count=5,
    )
    test_db.add(metadata)
    test_db.commit()

    cache_manager = CacheManager(test_db, cache_ttl_minutes=30)
    assert not cache_manager.is_cache_valid()


def test_update_cache(test_db):
    """Test updating cache with giveaways"""
    giveaways = [
        Giveaway("Test 1", "https://gleam.io/test1", "Description 1"),
        Giveaway("Test 2", "https://gleam.io/test2", "Description 2"),
    ]

    cache_manager = CacheManager(test_db)
    cache_manager.update_cache(giveaways)

    # Verify giveaways were stored
    stored = test_db.query(GiveawayModel).all()
    assert len(stored) == 2
    assert stored[0].title == "Test 1"
    assert stored[1].title == "Test 2"

    # Verify metadata was updated
    metadata = test_db.query(ScraperMetadata).first()
    assert metadata is not None
    assert metadata.last_scrape_count == 2


def test_get_cached_giveaways(test_db):
    """Test retrieving cached giveaways"""
    # Add giveaways to database
    giveaway1 = GiveawayModel(
        id="test1",
        title="Test 1",
        url="https://gleam.io/test1",
        description="Description 1",
    )
    giveaway2 = GiveawayModel(
        id="test2",
        title="Test 2",
        url="https://gleam.io/test2",
        description="Description 2",
    )
    test_db.add(giveaway1)
    test_db.add(giveaway2)

    # Add recent metadata
    metadata = ScraperMetadata(
        last_successful_scrape=datetime.utcnow(),
        last_scrape_count=2,
    )
    test_db.add(metadata)
    test_db.commit()

    cache_manager = CacheManager(test_db)
    cached = cache_manager.get_cached_giveaways()

    assert cached is not None
    assert len(cached) == 2
    assert cached[0].title == "Test 1"
    assert cached[1].title == "Test 2"
