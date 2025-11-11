"""
Unit tests for parser logic.
"""

from pathlib import Path

import pytest

from scraper.parser import parse_cards

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_parse_cards_returns_expected_payloads():
    html = load_fixture("sample_page.html")
    cards = parse_cards(html)

    assert cards, "Expected at least one card"
    first = cards[0]

    assert first.card_url.startswith("https://www.fut.gg/players/")
    assert first.image_url.startswith("https://")
    assert first.name
    assert isinstance(first.rating, int)
    assert first.version
    assert first.player_slug in first.card_slug