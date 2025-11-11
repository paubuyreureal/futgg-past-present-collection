"""
Pagination utilities for iterating FUT.GG pages until no cards remain.
"""

from __future__ import annotations

from typing import Iterable, Iterator, Tuple

import requests
from requests import Response, Session

from .client import fetch_page
from .config import get_settings

_settings = get_settings()


def build_page_url(page_number: int) -> str:
    """Return the absolute URL for a given page."""
    if page_number <= 1:
        return _settings.base_url
    return f"{_settings.base_url}?page={page_number}"


def iter_pages(
    session: Session,
    *,
    max_pages: int | None = None,
) -> Iterator[Tuple[int, Response]]:
    """
    Yield (page_number, response) pairs until we hit the configured max pages
    or the site returns a 404/410 (no more pages).

    The caller is responsible for breaking once the parsed content is empty.
    """
    limit = max_pages or _settings.max_pages
    page_number = 1

    while True:
        if limit is not None and page_number > limit:
            break

        url = build_page_url(page_number)
        try:
            response = fetch_page(session, url)
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code in {404, 410}:
                break
            raise
        yield page_number, response
        page_number += 1

