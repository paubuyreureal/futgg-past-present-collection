"""
Player-related Pydantic schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict

from .card import Card


class PlayerListItem(BaseModel):
    """Player representation for the list page."""

    model_config = ConfigDict(from_attributes=True)
    
    slug: str
    display_name: str
    base_card_image_url: str | None
    base_card_rating: int | None
    any_in_club: bool
    in_club_count: int = Field(description="Number of cards marked in_club")
    total_cards: int = Field(description="Total number of cards for this player")

    # class Config:
    #     from_attributes = True


class PlayerDetail(BaseModel):
    """Player representation for the detail page."""

    model_config = ConfigDict(from_attributes=True)
    
    slug: str
    display_name: str
    in_club_count: int = Field(description="Number of cards marked in_club")
    total_cards: int = Field(description="Total number of cards for this player")
    cards: list[Card] = Field(description="All cards for this player")

    # class Config:
    #     from_attributes = True