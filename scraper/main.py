"""
CLI entry point: orchestrates fetch → parse → store workflow.
"""

from __future__ import annotations

import logging
from contextlib import suppress

from scraper.client import throttled_session
from scraper.config import get_settings
from scraper.pagination import iter_pages
from scraper.parser import ParseError, parse_cards
from scraper.storage import CardPayload, upsert_players_and_cards, normalize_duplicate_display_names

settings = get_settings()

logger = logging.getLogger("ScrapeFutGG")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)
logger.setLevel(getattr(logging, settings.log_level, logging.INFO))


def main() -> None:
    logger.info("Starting scrape for %s", settings.base_url)

    total_cards = 0
    with throttled_session() as session:
        for page_number, response in iter_pages(session):
            logger.info("Fetched page %s (%s bytes)", page_number, len(response.text))
            try:
                cards = parse_cards(response.text)
            except ParseError as exc:
                logger.error("Parse error on page %s: %s", page_number, exc)
                continue

            if not cards:
                logger.info("No cards found on page %s; stopping.", page_number)
                break

            payloads = [CardPayload(**card.__dict__) for card in cards]  # type: ignore[arg-type]
            upsert_players_and_cards(payloads)
            total_cards += len(cards)
            logger.info("Stored %s cards (total %s)", len(cards), total_cards)

        updated = normalize_duplicate_display_names()
    if updated:
        logger.info("Normalized %s duplicate display names.", updated)
    logger.info("Scrape complete: %s cards processed", total_cards)


if __name__ == "__main__":
    main()

