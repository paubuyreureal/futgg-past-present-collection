"""
Scraper trigger endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks

from app.tasks.scraper_task import run_scraper_task, is_scraping

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("", status_code=202)
def trigger_scrape(background_tasks: BackgroundTasks) -> dict[str, str]:
    """
    Trigger a background scrape of the FUT.GG site.
    
    Returns immediately with status "accepted". The scraper runs in the background.
    """
    background_tasks.add_task(run_scraper_task)
    return {"status": "accepted", "message": "Scrape job started"}


@router.get("/status")
def get_scrape_status() -> dict[str, bool]:
    """
    Check if a scrape is currently in progress.
    
    Returns:
    - in_progress: True if scraping is active, False otherwise
    """
    return {"in_progress": is_scraping()}