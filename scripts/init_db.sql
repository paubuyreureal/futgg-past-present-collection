-- scripts/init_db.sql
-- Schema bootstrap for the ScrapeFutGG project.
-- Run after connecting to your target database (psql, pgAdmin, etc.).

BEGIN;

CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    -- Normalised identifier derived from the FUT.GG player slug (e.g., "claudia-pina").
    slug TEXT NOT NULL,
    display_name TEXT NOT NULL,
    any_in_club BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ux_players_slug UNIQUE (slug)
);

CREATE TABLE IF NOT EXISTS player_cards (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players (id) ON DELETE CASCADE,
    card_slug TEXT NOT NULL,
    name TEXT NOT NULL,
    rating INTEGER NOT NULL,
    version TEXT NOT NULL,
    card_url TEXT NOT NULL,
    image_url TEXT,
    in_club BOOLEAN NOT NULL DEFAULT FALSE,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ux_player_cards_slug UNIQUE (card_slug),
);

CREATE INDEX IF NOT EXISTS ix_player_cards_player_id
    ON player_cards (player_id);

CREATE INDEX IF NOT EXISTS ix_player_cards_in_club
    ON player_cards (in_club);

CREATE INDEX IF NOT EXISTS ix_players_any_in_club
    ON players (any_in_club);

COMMIT;