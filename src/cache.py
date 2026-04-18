"""
Cache management for giveaways
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from .database import Giveaway as GiveawayModel, ScraperMetadata
from .scraper import GleamScraper, Giveaway

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL", "30"))


class CacheManager:
    """Manages caching of giveaways with auto-refresh logic"""

    def __init__(self, db: Session, cache_ttl_minutes: int = CACHE_TTL_MINUTES):
        self.db = db
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)

    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        metadata = self.db.query(ScraperMetadata).first()
        if not metadata or not metadata.last_successful_scrape:
            return False

        age = datetime.utcnow() - metadata.last_successful_scrape
        is_valid = age < self.cache_ttl
        logger.info(
            f"Cache age: {age.total_seconds():.0f}s, "
            f"TTL: {self.cache_ttl.total_seconds():.0f}s, Valid: {is_valid}"
        )
        return is_valid

    def get_cached_giveaways(self) -> Optional[List[Giveaway]]:
        """Get cached giveaways if cache is valid"""
        if not self.is_cache_valid():
            return None

        try:
            db_giveaways = self.db.query(GiveawayModel).all()
            return [Giveaway(g.title, g.url, g.description) for g in db_giveaways]
        except Exception as e:
            logger.error(f"Error retrieving cached giveaways: {e}")
            return None

    def update_cache(self, giveaways: List[Giveaway]) -> None:
        """Update cache with new giveaways"""
        try:
            # Clear old giveaways
            self.db.query(GiveawayModel).delete()

            # Add new giveaways
            for giveaway in giveaways:
                # Create a simple ID from URL
                giveaway_id = giveaway.url.split("/")[-1] or giveaway.title[:20]

                db_giveaway = GiveawayModel(
                    id=giveaway_id,
                    title=giveaway.title,
                    url=giveaway.url,
                    description=giveaway.description,
                    last_scraped_at=datetime.utcnow(),
                )
                self.db.merge(db_giveaway)

            # Update metadata
            metadata = self.db.query(ScraperMetadata).first()
            if not metadata:
                metadata = ScraperMetadata()
                self.db.add(metadata)

            metadata.last_successful_scrape = datetime.utcnow()
            metadata.last_scrape_count = len(giveaways)
            metadata.updated_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"Cache updated with {len(giveaways)} giveaways")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating cache: {e}")
            raise

    def get_giveaways(
        self,
        force_refresh: bool = False,
        scraper_mode: Optional[str] = None,
        playwright_headless: Optional[bool] = None,
    ) -> List[Giveaway]:
        """Get giveaways with auto-refresh logic"""
        # Try to get cached giveaways if not forcing refresh
        if not force_refresh:
            cached = self.get_cached_giveaways()
            if cached:
                logger.info(f"Returning {len(cached)} cached giveaways")
                return cached

        # Scrape fresh data
        logger.info("Cache miss or force refresh, scraping fresh data...")
        scraper_kwargs = {}
        if scraper_mode:
            scraper_kwargs["mode"] = scraper_mode
        if playwright_headless is not None:
            scraper_kwargs["playwright_headless"] = playwright_headless
        scraper = GleamScraper(**scraper_kwargs)
        giveaways = scraper.scrape_all_giveaways()

        # Update cache
        self.update_cache(giveaways)

        return giveaways
