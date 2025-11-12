"""
Application configuration.

Reuses scraper configuration and adds FastAPI-specific settings.
"""

from __future__ import annotations

from scraper.config import get_settings as get_scraper_settings

# Re-export scraper settings
get_settings = get_scraper_settings
