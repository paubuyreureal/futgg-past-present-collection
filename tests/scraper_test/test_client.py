"""
Unit tests for HTTP client logic.
"""

import pytest
from unittest.mock import Mock, patch
import requests

from scraper.client import build_session, fetch_page, FetchError


def test_build_session_has_default_headers():
    session = build_session()
    assert "User-Agent" in session.headers
    assert "Accept" in session.headers


def test_fetch_page_success(mocker):
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>...</html>"
    mock_session.get.return_value = mock_response
    
    mocker.patch("time.sleep")  # skip delay in tests
    
    result = fetch_page(mock_session, "https://example.com")
    assert result == mock_response
    mock_session.get.assert_called_once_with("https://example.com", timeout=15)


def test_fetch_page_retries_on_connection_error(mocker):
    mock_session = Mock()
    mock_session.get.side_effect = [
        requests.ConnectionError(),
        requests.ConnectionError(),
        Mock(status_code=200, text="<html>...</html>"),
    ]
    
    mocker.patch("time.sleep")
    
    result = fetch_page(mock_session, "https://example.com")
    assert result.status_code == 200
    assert mock_session.get.call_count == 3


def test_fetch_page_raises_on_500(mocker):
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 500
    mock_session.get.return_value = mock_response
    
    mocker.patch("time.sleep")
    
    with pytest.raises(FetchError):
        fetch_page(mock_session, "https://example.com")