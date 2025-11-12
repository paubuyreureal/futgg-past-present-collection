"""
FastAPI application entry point.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cards_router, player_router, players_router, scrape_router

app = FastAPI(
    title="PastPresent Collection API",
    description="API for managing FC Barcelona past and present player cards from FUT.GG",
    version="1.0.0",
)

# CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(players_router)
app.include_router(player_router)
app.include_router(cards_router)
app.include_router(scrape_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": "PastPresent Collection API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}