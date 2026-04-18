"""
Stable service layer for external applications.
"""

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from src.cache import CacheManager
from src.database import SessionLocal, init_db
from src.scraper import Giveaway

VALID_SCRAPER_MODES = {"auto", "requests", "browser"}


@dataclass(frozen=True)
class Competition:
    """Serializable competition model for external consumers."""

    title: str
    url: str
    description: str

    @classmethod
    def from_giveaway(cls, giveaway: Giveaway) -> "Competition":
        return cls(
            title=giveaway.title,
            url=giveaway.url,
            description=giveaway.description or "",
        )


def init_database() -> None:
    """Create database tables for scraper/cache metadata."""
    init_db()


def list_competitions(
    force_refresh: bool = False,
    scraper_mode: Optional[str] = None,
    playwright_headless: Optional[bool] = None,
) -> List[Competition]:
    """
    Return competitions using cached data when valid, or scrape fresh data.
    """
    if scraper_mode is not None and scraper_mode not in VALID_SCRAPER_MODES:
        raise ValueError(
            f"Invalid scraper_mode: {scraper_mode!r}. "
            f"Expected one of: {sorted(VALID_SCRAPER_MODES)}"
        )

    db = SessionLocal()
    try:
        cache_manager = CacheManager(db)
        giveaways = cache_manager.get_giveaways(
            force_refresh=force_refresh,
            scraper_mode=scraper_mode,
            playwright_headless=playwright_headless,
        )
        return [Competition.from_giveaway(giveaway) for giveaway in giveaways]
    finally:
        db.close()


def refresh_competitions(
    scraper_mode: Optional[str] = None, playwright_headless: Optional[bool] = None
) -> List[Competition]:
    """Force-refresh competitions from gleam.io."""
    return list_competitions(
        force_refresh=True,
        scraper_mode=scraper_mode,
        playwright_headless=playwright_headless,
    )


def competitions_to_dicts(competitions: List[Competition]) -> List[Dict[str, str]]:
    """Convert competition objects to JSON-friendly dictionaries."""
    return [asdict(competition) for competition in competitions]

