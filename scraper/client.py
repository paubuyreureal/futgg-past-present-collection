"""
HTTP client helpers (session, headers, retries, polite throttling).
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

import requests
from requests import Response, Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import get_settings

_settings = get_settings()

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": _settings.user_agent
    or "ScrapeFutGG/1.0 (+https://github.com/paubuyreureal/ScrapeFutGG)",
}


def build_session() -> Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


@contextmanager
def throttled_session() -> Iterator[Session]:
    session = build_session()
    try:
        yield session
    finally:
        session.close()


class FetchError(RuntimeError):
    pass


@retry(
    reraise=True,
    retry=retry_if_exception_type((requests.RequestException, FetchError)),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(5),
)
def fetch_page(session: Session, url: str) -> Response:
    response = session.get(url, timeout=15)
    if response.status_code >= 500:
        raise FetchError(f"Server error {response.status_code} for {url}")
    if response.status_code != requests.codes.ok:  # type: ignore[attr-defined]
        response.raise_for_status()
    time.sleep(_settings.scrape_delay)
    return response