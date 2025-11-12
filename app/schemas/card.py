"""
Card-related Pydantic schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Card(BaseModel):
    """Card representation for API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    card_slug: str
    name: str
    rating: int
    version: str
    image_url: str | None
    card_url: str
    in_club: bool

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models


class CardUpdate(BaseModel):
    """Request schema for updating a card's in_club status."""
    
    in_club: bool