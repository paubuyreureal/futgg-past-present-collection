/**
 * Player detail page component.
 * 
 * This component:
 * - Displays detailed information for a single player
 * - Shows player's display_name and card count (in_club/total)
 * - Renders all player cards in a grid (4 per row on desktop)
 * - Displays card image, version, and in_club toggle switch for each card
 * - Handles clicking card images to redirect to fut.gg card URL
 * - Updates card in_club status via API when toggle is switched
 * - Fetches player data based on slug from URL parameter
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPlayer, updateCard } from '../api/client';

function PlayerDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingCards, setUpdatingCards] = useState(new Set());

  useEffect(() => {
    const fetchPlayer = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPlayer(slug);
        setPlayer(data);
      } catch (err) {
        console.error('Failed to fetch player:', err);
        setError('Player not found');
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      fetchPlayer();
    }
  }, [slug]);

  const handleCardClick = (cardUrl) => {
    window.open(cardUrl, '_blank', 'noopener,noreferrer');
  };

  const handleToggleInClub = async (cardSlug, currentStatus) => {
    const newStatus = !currentStatus;
    
    // Optimistic update
    setPlayer((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        cards: prev.cards.map((card) =>
          card.card_slug === cardSlug ? { ...card, in_club: newStatus } : card
        ),
        in_club_count: prev.in_club_count + (newStatus ? 1 : -1),
      };
    });

    // Track updating state
    setUpdatingCards((prev) => new Set(prev).add(cardSlug));

    try {
      await updateCard(cardSlug, newStatus);
    } catch (err) {
      console.error('Failed to update card:', err);
      // Revert optimistic update on error
      setPlayer((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          cards: prev.cards.map((card) =>
            card.card_slug === cardSlug ? { ...card, in_club: currentStatus } : card
          ),
          in_club_count: prev.in_club_count + (newStatus ? -1 : 1),
        };
      });
      alert('Failed to update card status. Please try again.');
    } finally {
      setUpdatingCards((prev) => {
        const next = new Set(prev);
        next.delete(cardSlug);
        return next;
      });
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading player...</p>
        </div>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p className="text-lg text-red-600 mb-4">{error || 'Player not found'}</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Player List
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back button */}
      <button
        onClick={() => navigate('/')}
        className="mb-6 text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        <span>←</span> Back to Player List
      </button>

      {/* Player header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">{player.display_name}</h1>
        <p className="text-lg text-gray-600">
          Cards in club: <span className="font-semibold">{player.in_club_count}/{player.total_cards}</span>
        </p>
      </div>

      {/* Cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {player.cards.map((card) => (
          <div
            key={card.card_slug}
            className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 border border-gray-200"
          >
            {/* Card image (clickable) */}
            <div
              onClick={() => handleCardClick(card.card_url)}
              className="mb-3 cursor-pointer hover:opacity-80 transition-opacity"
            >
              {card.image_url ? (
                <img
                  src={card.image_url}
                  alt={`${card.name} - ${card.rating}`}
                  className="w-full h-auto rounded"
                />
              ) : (
                <div className="w-full aspect-[3/4] bg-gray-200 rounded flex items-center justify-center text-gray-400">
                  No Image
                </div>
              )}
            </div>

            {/* Card info */}
            <div className="space-y-2">
              {/* Version */}
              <p className="text-sm font-semibold text-gray-700 text-center">
                {card.version}
              </p>

              {/* Rating (optional, if you want to show it) */}
              <p className="text-xs text-gray-500 text-center">
                Rating: {card.rating}
              </p>

              {/* In club toggle */}
              <div className="flex items-center justify-center gap-2 pt-2">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={card.in_club}
                    onChange={() => handleToggleInClub(card.card_slug, card.in_club)}
                    disabled={updatingCards.has(card.card_slug)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  <span className="ml-3 text-sm text-gray-700">
                    {card.in_club ? 'In Club' : 'Not In Club'}
                  </span>
                </label>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty state */}
      {player.cards.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600">No cards found for this player</p>
        </div>
      )}
    </div>
  );
}

export default PlayerDetail;