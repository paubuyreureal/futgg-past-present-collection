"""
Quick helpers to toggle and inspect player cards.
"""

from __future__ import annotations

from scraper.storage import session_scope
from scraper.models import PlayerCard


def set_in_club(card_slugs: list[str], value: bool = True) -> int:
    """Toggle the in_club flag for the given card slugs."""
    with session_scope() as session:
        cards = (
            session.query(PlayerCard)
            .filter(PlayerCard.card_slug.in_(card_slugs))
            .all()
        )
        for card in cards:
            card.in_club = value
        return len(cards)


from scraper.storage import session_scope
from scraper.models import Player, PlayerCard

def get_cards(display_name: str) -> list[tuple[str, int, str, bool]]:
    """
    Fetch card info for the player with the given display_name.
    If multiple players have that name, list their ids/slugs so the caller can disambiguate.
    """
    with session_scope() as session:
        players = (
            session.query(Player)
            .filter(Player.display_name == display_name)
            .all()
        )

        if not players:
            print(f"No player found with display name {display_name!r}.")
            return []

        if len(players) > 1:
            print(f"Multiple players found with display name {display_name!r}:")
            for player in players:
                print(f" - id={player.id}, slug={player.slug}, display_name={player.display_name}")
            print("Re-run using one of the listed slugs or ids to get card details.")
            return []

        player = players[0]
        cards = (
            session.query(PlayerCard)
            .filter(PlayerCard.player_id == player.id)
            .order_by(PlayerCard.rating.desc(), PlayerCard.version)
            .all()
        )

        return [
            (card.name, card.rating, card.version, card.in_club)
            for card in cards
        ]


if __name__ == "__main__":
    # Example usage: toggle and then show a player's cards
    toggled = set_in_club(
        [
            "231443-ousmane-dembele/26-50563091",
            #"231443-ousmane-dembele/26-231443",
        ],
        value=True,
    )
    print(f"Toggled {toggled} cards")

    for name, rating, version, in_club in get_cards("Dembélé"):
        status = "✅" if in_club else "❌"
        print(f"{status} {name} {rating} - {version}")


