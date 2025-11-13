/**
 * Player list page component (home page).
 * 
 * This component:
 * - Displays a list of all players with their base card images
 * - Implements search functionality (accent-insensitive name search)
 * - Provides filtering by in_club status (all/in_club/not_in_club)
 * - Supports sorting by base card rating (ascending/descending)
 * - Shows player display_name, base_card_image, any_in_club indicator, and card count
 * - Includes a button to trigger the scraper (with loading state)
 * - Navigates to PlayerDetail page when a player is clicked
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlayers, triggerScrape, getScrapeStatus } from '../api/client';

function PlayerList() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [inClubFilter, setInClubFilter] = useState('all');
  const [sort, setSort] = useState('desc');
  const [scraping, setScraping] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState(false);
  
  const navigate = useNavigate();

  // Fetch players when filters/search/sort change
  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true);
      try {
        const data = await getPlayers({
          search: search || undefined,
          in_club: inClubFilter,
          sort,
        });
        setPlayers(data);
      } catch (error) {
        console.error('Failed to fetch players:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, [search, inClubFilter, sort]);

  // Poll scrape status when scraping
  useEffect(() => {
    if (!scraping) return;

    const interval = setInterval(async () => {
      try {
        const status = await getScrapeStatus();
        setScrapeStatus(status.in_progress);
        
        // If scraping finished, refresh player list
        if (!status.in_progress) {
          setScraping(false);
          // Refresh players
          const data = await getPlayers({
            search: search || undefined,
            in_club: inClubFilter,
            sort,
          });
          setPlayers(data);
        }
      } catch (error) {
        console.error('Failed to check scrape status:', error);
        setScraping(false);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [scraping, search, inClubFilter, sort]);

  const handleScrape = async () => {
    setScraping(true);
    setScrapeStatus(true);
    try {
      await triggerScrape();
      // Status polling will handle the rest
    } catch (error) {
      console.error('Failed to trigger scrape:', error);
      setScraping(false);
      setScrapeStatus(false);
    }
  };

  const handlePlayerClick = (slug) => {
    navigate(`/players/${slug}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header with title and scrape button */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">FC Barcelona - Past & Present</h1>
        <button
          onClick={handleScrape}
          disabled={scraping}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {scraping ? 'Scraping...' : 'Update Database'}
        </button>
      </div>

      {/* Loading overlay when scraping */}
      {scraping && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-lg font-semibold">Scraping in progress...</p>
              <p className="text-sm text-gray-600 mt-2">Please wait while we update the database</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters and search */}
      <div className="mb-6 space-y-4 md:space-y-0 md:flex md:gap-4">
        {/* Search input */}
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search players..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter dropdown */}
        <select
          value={inClubFilter}
          onChange={(e) => setInClubFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Players</option>
          <option value="in_club">In Club</option>
          <option value="not_in_club">Not In Club</option>
        </select>

        {/* Sort dropdown */}
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="desc">Rating: High to Low</option>
          <option value="asc">Rating: Low to High</option>
        </select>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading players...</p>
        </div>
      )}

      {/* Player list */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {players.map((player) => (
            <div
              key={player.slug}
              onClick={() => handlePlayerClick(player.slug)}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer p-4 border border-gray-200 hover:border-blue-500"
            >
              {/* Player image */}
              <div className="mb-3 flex justify-center">
                {player.base_card_image_url ? (
                  <img
                    src={player.base_card_image_url}
                    alt={player.display_name}
                    className="w-24 h-24 object-contain"
                  />
                ) : (
                  <div className="w-24 h-24 bg-gray-200 rounded flex items-center justify-center text-gray-400">
                    No Image
                  </div>
                )}
              </div>

              {/* Player name */}
              <h2 className="text-lg font-semibold text-gray-900 mb-2 text-center">
                {player.display_name}
              </h2>

              {/* Rating */}
              {player.base_card_rating && (
                <p className="text-sm text-gray-600 text-center mb-2">
                  Rating: {player.base_card_rating}
                </p>
              )}

              {/* In club indicator and count */}
              <div className="flex items-center justify-center gap-2">
                <span
                  className={`inline-block w-3 h-3 rounded-full ${
                    player.any_in_club ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                  title={player.any_in_club ? 'Has cards in club' : 'No cards in club'}
                />
                <span className="text-sm text-gray-600">
                  {player.in_club_count}/{player.total_cards}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && players.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">No players found</p>
          <p className="text-gray-500 text-sm mt-2">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}

export default PlayerList;