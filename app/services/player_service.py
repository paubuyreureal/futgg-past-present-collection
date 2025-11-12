"""
Player query and business logic.
"""

from __future__ import annotations

from typing import Literal

from sqlalchemy import func, or_, select, Integer
from sqlalchemy.orm import Session

from app.schemas.player import PlayerDetail, PlayerListItem
from scraper.models import Player, PlayerCard


def get_players_list(
    db: Session,
    *,
    search: str | None = None,
    in_club_filter: Literal["all", "in_club", "not_in_club"] | None = None,
    sort_by_rating: Literal["asc", "desc"] = "desc",
) -> list[PlayerListItem]:
    """
    Get paginated list of players with filters and sorting.
    
    Parameters
    ----------
    db
        Database session
    search
        Search term for display_name (accent-insensitive, case-insensitive)
    in_club_filter
        Filter by any_in_club status
    sort_by_rating
        Sort order by base_card_rating
    """
    query = select(Player)
    
    # Apply search filter (accent-insensitive)
    if search:
        search_normalized = search.lower().strip()
        # Use unaccent if available, otherwise fallback to ILIKE
        try:
            query = query.where(
                func.unaccent(func.lower(Player.display_name)).contains(
                    func.unaccent(search_normalized)
                )
            )
        except Exception:
            # Fallback if unaccent extension not available
            query = query.where(
                func.lower(Player.display_name).contains(search_normalized)
            )
    
    # Apply in_club filter
    if in_club_filter == "in_club":
        query = query.where(Player.any_in_club == True)
    elif in_club_filter == "not_in_club":
        query = query.where(Player.any_in_club == False)
    
    # Apply sorting
    if sort_by_rating == "desc":
        query = query.order_by(Player.base_card_rating.desc().nulls_last())
    else:
        query = query.order_by(Player.base_card_rating.asc().nulls_last())
    
    players = db.scalars(query).all()
    
    # Build response with card counts
    result = []
    for player in players:
        # Count cards
        card_counts = db.execute(
            select(
                func.count(PlayerCard.id).label("total"),
                func.sum(func.cast(PlayerCard.in_club, Integer)).label("in_club"),
            ).where(PlayerCard.player_id == player.id)
        ).one()
        
        total_cards = card_counts.total or 0
        in_club_count = int(card_counts.in_club or 0)
        
        result.append(
            PlayerListItem(
                slug=player.slug,
                display_name=player.display_name,
                base_card_image_url=player.base_card_image_url,
                base_card_rating=player.base_card_rating,
                any_in_club=player.any_in_club,
                in_club_count=in_club_count,
                total_cards=total_cards,
            )
        )
    
    return result


def get_player_by_slug(db: Session, slug: str) -> PlayerDetail | None:
    """
    Get a single player with all their cards.
    
    Parameters
    ----------
    db
        Database session
    slug
        Player slug identifier
    """
    player = db.scalar(select(Player).where(Player.slug == slug))
    if not player:
        return None
    
    # Get all cards for this player
    cards = db.scalars(
        select(PlayerCard)
        .where(PlayerCard.player_id == player.id)
        .order_by(PlayerCard.rating.desc(), PlayerCard.version)
    ).all()
    
    # Count in_club cards
    card_counts = db.execute(
        select(
            func.count(PlayerCard.id).label("total"),
            func.sum(func.cast(PlayerCard.in_club, Integer)).label("in_club"),
        ).where(PlayerCard.player_id == player.id)
    ).one()
    
    total_cards = card_counts.total or 0
    in_club_count = int(card_counts.in_club or 0)
    
    from app.schemas.card import Card
    
    return PlayerDetail(
        slug=player.slug,
        display_name=player.display_name,
        in_club_count=in_club_count,
        total_cards=total_cards,
        cards=[Card.model_validate(card) for card in cards],
    )