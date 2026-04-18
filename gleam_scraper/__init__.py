"""
Public package interface for integrating gleam-scraper into other applications.
"""

from .service import (
    Competition,
    competitions_to_dicts,
    init_database,
    list_competitions,
    refresh_competitions,
)

__all__ = [
    "Competition",
    "competitions_to_dicts",
    "init_database",
    "list_competitions",
    "refresh_competitions",
]

