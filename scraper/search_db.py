from pprint import pprint

from scraper.storage import session_scope
from scraper.models import Player, PlayerCard


def get_cards_by_display_name(display_name: str) -> list[dict]:
    with session_scope() as session:
        player = (
            session.query(Player)
            .filter(Player.display_name == display_name)
            .one_or_none()
        )
        if player is None:
            return []

        cards = (
            session.query(PlayerCard)
            .filter(PlayerCard.player_id == player.id)
            .order_by(PlayerCard.rating.desc(), PlayerCard.version)
            .all()
        )

        return [
            {
                "name": card.name,
                "rating": card.rating,
                "version": card.version,
                "card_url": card.card_url,
                "image_url": card.image_url,
                "in_club": card.in_club,
                "scraped_at": card.scraped_at,
                "last_seen_at": card.last_seen_at,
            }
            for card in cards
        ]


if __name__ == "__main__":
    cards = get_cards_by_display_name("Denis Suárez")
    if not cards:
        print("No cards found for Denis Suárez.")
    else:
        pprint(cards)