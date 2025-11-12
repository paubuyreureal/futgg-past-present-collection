"""
Background task to run the scraper.
"""

from __future__ import annotations

import logging
import threading

from scraper.main import main

logger = logging.getLogger("ScrapeFutGG")

# Simple flag to track scraping status
_scraping_lock = threading.Lock()
_is_scraping = False


def is_scraping() -> bool:
    """Check if scraping is currently in progress."""
    with _scraping_lock:
        return _is_scraping


def run_scraper_task() -> None:
    """
    Background task that runs the scraper.
    
    This function is called by FastAPI's BackgroundTasks and runs
    the scraper's main() function to update the database.
    """
    global _is_scraping
    try:
        with _scraping_lock:
            _is_scraping = True
        logger.info("Starting background scrape task")
        main()
        logger.info("Background scrape task completed successfully")
    except Exception as exc:
        logger.error("Background scrape task failed: %s", exc, exc_info=True)
        raise
    finally:
        with _scraping_lock:
            _is_scraping = False