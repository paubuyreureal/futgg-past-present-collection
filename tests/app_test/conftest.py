"""
Pytest fixtures for API testing.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from scraper.models import Base, Player, PlayerCard
from scraper.storage.connection import get_engine
from app.main import app


# Test database URL (use in-memory SQLite for speed, or a test PostgreSQL DB)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Uses an in-memory SQLite database for speed.
    """
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def sample_player(db_session: Session) -> Player:
    """Create a sample player for testing."""
    player = Player(
        slug="test-player",
        display_name="Test Player",
        any_in_club=False,
        base_card_slug="test-card",
        base_card_rating=85,
        base_card_version="Rare",
        base_card_image_url="https://example.com/image.jpg",
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


@pytest.fixture(scope="function")
def sample_cards(db_session: Session, sample_player: Player) -> list[PlayerCard]:
    """Create sample cards for a player."""
    cards = [
        PlayerCard(
            player_id=sample_player.id,
            card_slug="test-card-1",
            name="Test Player",
            rating=85,
            version="Rare",
            card_url="https://www.fut.gg/test-card-1",
            image_url="https://example.com/card1.jpg",
            in_club=True,
        ),
        PlayerCard(
            player_id=sample_player.id,
            card_slug="test-card-2",
            name="Test Player",
            rating=87,
            version="Common",
            card_url="https://www.fut.gg/test-card-2",
            image_url="https://example.com/card2.jpg",
            in_club=False,
        ),
    ]
    db_session.add_all(cards)
    db_session.commit()
    for card in cards:
        db_session.refresh(card)
    return cards


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a test client with a database session override.
    """
    # Ensure tables exist in the session's database
    Base.metadata.create_all(db_session.bind)
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close the session, it's managed by the fixture
    
    from app.dependencies import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()