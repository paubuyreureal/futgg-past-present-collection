"""
Integration tests for the full scraping pipeline.
"""

import pytest
from unittest.mock import Mock, patch

from scraper.main import main
from scraper.parser import parse_cards


def test_full_scrape_flow_mocked(mocker):
    """Test the main() function with mocked HTTP calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><a href='/players/123-test/26-123/'><img alt='Test - 85 - Rare' src='img.webp'></a></html>"
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    
    mocker.patch("scraper.client.throttled_session", return_value=Mock(__enter__=lambda _: mock_session, __exit__=lambda *_: None))
    mocker.patch("scraper.storage.upsert_players_and_cards")
    mocker.patch("scraper.storage.normalize_duplicate_display_names", return_value=0)
    mocker.patch("scraper.storage.assign_base_cards", return_value=0)
    mocker.patch("time.sleep")
    
    # Should not raise
    main()