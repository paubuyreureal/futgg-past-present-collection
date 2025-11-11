"""
BeautifulSoup parsing helpers that convert FUT.GG HTML into structured data.
"""

from __future__ import annotations

import re
from typing import Iterable, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .config import get_settings
from .storage import CardPayload

_settings = get_settings()
_CARD_HREF_RE = re.compile(r"^/players/([^/]+)/")
FUTGG_ROOT = "https://www.fut.gg"


class ParseError(RuntimeError):
    """Raised when we cannot interpret the FUT.GG card structure."""


def parse_cards(html: str) -> List[CardPayload]:
    """
    Parse a FUT.GG player listing page and return card payloads.

    Parameters
    ----------
    html:
        Raw HTML returned by FUT.GG for a Past & Present listing page.

    Returns
    -------
    list[CardPayload]
        Structured card data ready to be persisted.
    """
    soup = BeautifulSoup(html, "lxml")
    cards: list[CardPayload] = []
    seen_slugs: set[str] = set()

    for anchor in _iter_card_anchors(soup):
        try:
            payload = _parse_anchor(anchor)
        except ParseError:
            continue
        if payload.card_slug in seen_slugs:
            continue
        seen_slugs.add(payload.card_slug)
        cards.append(payload)

    return cards


def _iter_card_anchors(soup: BeautifulSoup) -> Iterable[Tag]:
    """
    Yield anchor tags that represent player cards.

    FUT.GG card markup is an <a> tag whose href starts with '/players/' and
    contains an <img> with an 'alt' field describing the card.
    """
    for anchor in soup.select("a[href^='/players/']"):
        if anchor.find("img", alt=True):
            yield anchor


def _parse_anchor(anchor: Tag) -> CardPayload:
    href = anchor.get("href")
    if not href:
        raise ParseError("Anchor missing href")

    parts = href.strip("/").split("/")
    if len(parts) < 3 or parts[0] != "players":
        raise ParseError(f"Unexpected player URL format: {href!r}")

    player_segment = parts[1]
    card_slug = "/".join(parts[1:])  # e.g. "231443-ousmane-dembele/26-50563091"
    player_slug = _derive_player_slug(player_segment)

    image = anchor.find("img", alt=True)
    if image is None:
        raise ParseError("Card anchor missing img/alt")

    alt_text = image["alt"].strip()
    name, rating, version = _split_alt_text(alt_text)

    card_url = urljoin(FUTGG_ROOT, href)
    raw_image_url = image.get("src") or image.get("data-src")
    if not raw_image_url:
        raise ParseError("Card image missing src/data-src")
    image_url = urljoin(FUTGG_ROOT, raw_image_url)

    return CardPayload(
        player_slug=player_slug,
        display_name=name,
        card_slug=card_slug,
        name=name,
        rating=rating,
        version=version,
        card_url=card_url,
        image_url=image_url,
    )


def _split_alt_text(alt_text: str) -> tuple[str, int, str]:
    """
    FUT.GG alt values look like 'Marc Cucurella - 85 - Ratings Reload'.

    We split on ' - ', casting the second token to int and joining the rest
    back into the version name in case it also contains hyphens.
    """
    parts = [part.strip() for part in alt_text.split(" - ") if part.strip()]
    if len(parts) < 3:
        raise ParseError(f"Unexpected alt text format: {alt_text!r}")

    name = parts[0]
    try:
        rating = int(parts[1])
    except ValueError as exc:
        raise ParseError(f"Cannot parse rating from alt text: {alt_text!r}") from exc
    version = " - ".join(parts[2:])

    return name, rating, version


def _derive_player_slug(card_slug: str) -> str:
    """
    Convert a card slug (e.g., '262531-claudia-pina') to a player slug ('claudia-pina').

    FUT.GG prefixes each card slug with a numeric ID; removing it groups
    variants of the same player together.
    """
    return re.sub(r"^\d+-", "", card_slug)
