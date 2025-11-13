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

import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getPlayers, triggerScrape, getScrapeStatus, getPlayerCounts } from '../api/client';

function PlayerList() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [inClubFilter, setInClubFilter] = useState('all');
  const [sort, setSort] = useState('desc');
  const [scraping, setScraping] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState(false);
  const [playerCounts, setPlayerCounts] = useState({ total: 0, in_club: 0 });
  
  const navigate = useNavigate();
  const location = useLocation();
  const hasRestoredFromState = useRef(false);
  const hasRestoredScroll = useRef(false);

  // Restore filters from location state when returning from player detail
  useEffect(() => {
    if (location.state?.filters && !hasRestoredFromState.current) {
      const { search: savedSearch, inClubFilter: savedFilter, sort: savedSort } = location.state.filters;
      
      // Update state
      if (savedSearch !== undefined) setSearch(savedSearch);
      if (savedFilter !== undefined) setInClubFilter(savedFilter);
      if (savedSort !== undefined) setSort(savedSort);
      
      // Mark as restored
      hasRestoredFromState.current = true;
      
      // Explicitly fetch players with restored filters
      const fetchPlayersWithFilters = async () => {
        setLoading(true);
        try {
          const data = await getPlayers({
            search: savedSearch || undefined,
            in_club: savedFilter || 'all',
            sort: savedSort || 'desc',
          });
          setPlayers(data);
        } catch (error) {
          console.error('Failed to fetch players:', error);
        } finally {
          setLoading(false);
          // Reset flag after restoration is complete
          hasRestoredFromState.current = false;
        }
      };
      
      fetchPlayersWithFilters();
    } else if (!location.state?.filters) {
      // Reset the flag when there's no state to restore
      hasRestoredFromState.current = false;
      hasRestoredScroll.current = false;  // Also reset scroll flag
    }
  }, [location.state]);

  // Fetch players when filters/search/sort change (skip if restoring from state)
  useEffect(() => {
    // Skip if we're currently restoring from location.state
    if (hasRestoredFromState.current) {
      return;
    }
    
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

  // Restore scroll position after players load (when returning from player detail)
  useEffect(() => {
    if (location.state?.scrollPosition && players.length > 0 && !loading && !hasRestoredScroll.current) {
      // Mark as restored
      hasRestoredScroll.current = true;
      
      // Small delay to ensure DOM is ready
      setTimeout(() => {
        window.scrollTo(0, location.state.scrollPosition);
        
        // Optionally scroll to specific player card
        if (location.state.playerSlug) {
          const playerElement = document.querySelector(`[data-player-slug="${location.state.playerSlug}"]`);
          if (playerElement) {
            playerElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      }, 100);
    }
  }, [players, loading, location.state]);


  // Fetch player counts on mount and when scraping finishes
  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const counts = await getPlayerCounts();
        setPlayerCounts(counts);
      } catch (error) {
        console.error('Failed to fetch player counts:', error);
      }
    };
    
    fetchCounts();
  }, [scraping]); // Refetch when scraping finishes


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
    // Save current state before navigating
    const scrollPosition = window.scrollY;
    navigate(`/players/${slug}`, {
      state: {
        filters: {
          search,
          inClubFilter,
          sort,
        },
        scrollPosition,
        playerSlug: slug,
      },
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header with title and scrape button */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <img 
            src="/favicon.png" 
            alt="FC Barcelona" 
            className="w-10 h-10"
          />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">FC Barcelona - Past & Present Collection</h1>
            <p className="text-lg text-gray-500 mt-1">
              {playerCounts.in_club} / {playerCounts.total} players in club
            </p>
          </div>
        </div>
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
          {players.map((player) => (
            <div
              key={player.slug}
              data-player-slug={player.slug}  // Add this for scrolling
              onClick={() => handlePlayerClick(player.slug)}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer pt-1 px-4 pb-4 border border-gray-200 hover:border-blue-500 flex flex-col"
            >
            {/* Player image - bigger */}
            <div className="flex justify-center">
              {player.base_card_image_url ? (
                <img
                  src={player.base_card_image_url}
                  alt={player.display_name}
                  className="w-64 h-64 object-contain"
                />
              ) : (
                <div className="w-64 h-64 bg-gray-200 rounded flex items-center justify-center text-gray-400">
                  No Image
                </div>
              )}
            </div>

            {/* Player name and counter in same row */}
            <div className="flex items-center justify-between gap-2 mt-2">
              <h2 className="text-lg font-semibold text-gray-900 flex-1 truncate">
                {player.display_name}
              </h2>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span
                  className={`inline-block w-3 h-3 rounded-full ${
                    player.any_in_club ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                  title={player.any_in_club ? 'Has cards in club' : 'No cards in club'}
                />
                <span className="text-base text-gray-600">
                  {player.in_club_count}/{player.total_cards}
                </span>
              </div>
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