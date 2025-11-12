"""
Pytest fixtures for API testing.
"""

import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from scraper.models import Base, Player, PlayerCard
from scraper.storage.connection import get_engine
from app.main import app


# Use a temporary file-based SQLite database
# This ensures all connections share the same database (unlike :memory:)
_test_db_file = None

def _get_test_db_url():
    """Get a temporary file-based SQLite database URL."""
    global _test_db_file
    if _test_db_file is None:
        fd, _test_db_file = tempfile.mkstemp(suffix='.db')
        os.close(fd)  # Close the file descriptor, we only need the path
    return f"sqlite:///{_test_db_file}"


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Uses a temporary file-based SQLite database so connections share the same DB.
    """
    db_url = _get_test_db_url()
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up: drop all tables but keep the file for other connections
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
    # Ensure tables exist (they should already exist from db_session fixture)
    engine = db_session.get_bind()
    Base.metadata.create_all(engine)
    
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


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Clean up the temporary test database file after all tests."""
    yield
    global _test_db_file
    if _test_db_file and os.path.exists(_test_db_file):
        try:
            os.unlink(_test_db_file)
        except Exception:
            pass  # Ignore cleanup errors