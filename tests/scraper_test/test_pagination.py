"""
Unit tests for pagination logic.
"""

import pytest
from unittest.mock import Mock

from scraper.pagination import build_page_url, iter_pages
from scraper.config import get_settings

settings = get_settings()


def test_build_page_url():
    assert build_page_url(1) == settings.base_url
    assert build_page_url(2) == f"{settings.base_url}?page=2"
    assert build_page_url(5) == f"{settings.base_url}?page=5"


def test_iter_pages_stops_on_404(mocker):
    mock_session = Mock()
    mock_response_1 = Mock()
    mock_response_1.status_code = 200
    mock_response_1.text = "<html>...</html>"
    
    mock_response_2 = Mock()
    mock_response_2.status_code = 404
    
    from requests import HTTPError
    mock_response_2.raise_for_status.side_effect = HTTPError(response=mock_response_2)
    mock_response_2.status_code = 404
    
    mocker.patch("scraper.pagination.fetch_page", side_effect=[
        mock_response_1,
        HTTPError(response=mock_response_2),
    ])
    
    pages = list(iter_pages(mock_session, max_pages=10))
    assert len(pages) == 1
    assert pages[0][0] == 1


def test_iter_pages_respects_max_pages(mocker):
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>...</html>"
    
    mocker.patch("scraper.pagination.fetch_page", return_value=mock_response)
    
    pages = list(iter_pages(mock_session, max_pages=3))
    assert len(pages) == 3