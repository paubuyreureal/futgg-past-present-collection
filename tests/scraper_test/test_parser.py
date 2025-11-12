"""
Unit tests for parser logic.
"""

from pathlib import Path

import pytest

from scraper.parser import ParseError, parse_cards, _parse_anchor, _split_alt_text, _derive_player_slug
from bs4 import BeautifulSoup

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


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


def test_parse_cards_handles_empty_page():
    html = "<html><body></body></html>"
    cards = parse_cards(html)
    assert cards == []


def test_split_alt_text_valid():
    name, rating, version = _split_alt_text("Marc Cucurella - 85 - Ratings Reload")
    assert name == "Marc Cucurella"
    assert rating == 85
    assert version == "Ratings Reload"


def test_split_alt_text_with_hyphens_in_version():
    name, rating, version = _split_alt_text("Player - 90 - Special - Edition - Card")
    assert name == "Player"
    assert rating == 90
    assert version == "Special - Edition - Card"


def test_split_alt_text_invalid_format():
    with pytest.raises(ParseError):
        _split_alt_text("Invalid format")
    
    with pytest.raises(ParseError):
        _split_alt_text("Name - not_a_number - Version")


def test_derive_player_slug():
    assert _derive_player_slug("231443-ousmane-dembele") == "ousmane-dembele"
    assert _derive_player_slug("41-iniesta") == "iniesta"
    assert _derive_player_slug("ronaldo") == "ronaldo"  # edge case