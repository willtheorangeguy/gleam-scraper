"""
Database configuration and models for gleam-scraper
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gleam_scraper.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Giveaway(Base):
    """Model for a gleam.io giveaway"""

    __tablename__ = "giveaways"

    id = Column(String(500), primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1000), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = Column(DateTime, default=datetime.utcnow, index=True)


class ScraperMetadata(Base):
    """Metadata about scraping operations"""

    __tablename__ = "scraper_metadata"

    id = Column(Integer, primary_key=True, index=True)
    last_successful_scrape = Column(DateTime, nullable=True, index=True)
    total_giveaways_scraped = Column(Integer, default=0)
    last_scrape_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def get_db() -> Session:
    """Dependency for getting a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
