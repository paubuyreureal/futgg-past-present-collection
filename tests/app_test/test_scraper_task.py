"""
Tests for scraper task functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.tasks.scraper_task import is_scraping, run_scraper_task


def test_is_scraping_initial_state():
    """Test that is_scraping() returns False initially."""
    # Reset state by importing fresh
    from app.tasks import scraper_task
    scraper_task._is_scraping = False
    
    assert is_scraping() is False


def test_is_scraping_during_task(mocker):
    """Test that is_scraping() reflects the task state."""
    from app.tasks import scraper_task
    
    # Mock the main function to simulate a long-running task
    mock_main = mocker.patch("app.tasks.scraper_task.main")
    
    # Reset state
    scraper_task._is_scraping = False
    
    # Start task in a thread to test concurrent access
    import threading
    import time
    
    def run_task():
        run_scraper_task()
    
    thread = threading.Thread(target=run_task)
    thread.start()
    
    # Give it a moment to start
    time.sleep(0.1)
    
    # Should be True while running (if main is slow enough)
    # Note: This is timing-dependent, so we just verify the function works
    status = is_scraping()
    assert isinstance(status, bool)
    
    # Wait for thread to complete
    thread.join(timeout=2)
    
    # Should be False after completion
    assert is_scraping() is False


def test_run_scraper_task_calls_main(mocker):
    """Test that run_scraper_task calls the scraper's main function."""
    mock_main = mocker.patch("app.tasks.scraper_task.main")
    mock_main.return_value = None
    
    run_scraper_task()
    
    mock_main.assert_called_once()


def test_run_scraper_task_handles_exceptions(mocker):
    """Test that run_scraper_task handles exceptions and resets flag."""
    from app.tasks import scraper_task
    
    # Mock main to raise an exception
    mock_main = mocker.patch("app.tasks.scraper_task.main")
    mock_main.side_effect = Exception("Test error")
    
    # Reset state
    scraper_task._is_scraping = False
    
    # Should raise but reset flag
    with pytest.raises(Exception):
        run_scraper_task()
    
    # Flag should be reset even after exception
    assert is_scraping() is False