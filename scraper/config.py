"""
Scraper configuration loader.

Reads environment variables (using python-dotenv), converts them to the
types we expect, and exposes a cached Settings object for the rest of
the project.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


# Load .env placed at the project root (one level above this file)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str
    base_url: str
    scrape_delay: float
    max_pages: Optional[int]
    log_level: str
    user_agent: Optional[str]


def _to_float(value: str | None, default: float) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"SCRAPE_DELAY must be a number, got {value!r}") from exc


def _to_int_or_none(value: str | None) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"MAX_PAGES must be an integer, got {value!r}") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    scrape_delay = _to_float(os.getenv("SCRAPE_DELAY"), default=1.0)
    max_pages = _to_int_or_none(os.getenv("MAX_PAGES"))
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    user_agent = os.getenv("USER_AGENT") or None

    if not database_url:
        raise ValueError("DATABASE_URL is required (set it in .env)")
    if not base_url:
        raise ValueError("BASE_URL is required (set it in .env)")

    return Settings(
        database_url=database_url,
        base_url=base_url,
        scrape_delay=scrape_delay,
        max_pages=max_pages,
        log_level=log_level,
        user_agent=user_agent,
    )


__all__ = ["Settings", "get_settings"]

if __name__ == "__main__":    
    print(get_settings())