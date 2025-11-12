"""
Background task to run the scraper.
"""

from __future__ import annotations

import logging

from scraper.main import main

logger = logging.getLogger("ScrapeFutGG")


def run_scraper_task() -> None:
    """
    Background task that runs the scraper.
    
    This function is called by FastAPI's BackgroundTasks and runs
    the scraper's main() function to update the database.
    """
    try:
        logger.info("Starting background scrape task")
        main()
        logger.info("Background scrape task completed successfully")
    except Exception as exc:
        logger.error("Background scrape task failed: %s", exc, exc_info=True)
        raise