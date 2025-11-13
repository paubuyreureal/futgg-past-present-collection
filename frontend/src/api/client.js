/**
 * API client configuration and functions.
 * 
 * This module:
 * - Creates and configures an Axios instance with base URL for FastAPI backend
 * - Defines API endpoint functions (getPlayers, getPlayer, updateCard, etc.)
 * - Handles request/response interceptors for error handling or auth if needed
 * - Centralizes all backend API communication
 */


import axios from 'axios';

// Base URL for API requests
// In development: uses Vite proxy (/api -> http://localhost:8000)
// In production: can be set via environment variable or use full URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Create Axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for adding auth tokens, etc. in the future)
apiClient.interceptors.request.use(
  (config) => {
    // Add any request modifications here (e.g., auth tokens)
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for global error handling)
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors (401, 404, 500, etc.)
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Get list of players with optional search, filtering, and sorting.
 * 
 * @param {Object} params - Query parameters
 * @param {string} [params.search] - Search term for player names
 * @param {'all'|'in_club'|'not_in_club'} [params.in_club='all'] - Filter by in_club status
 * @param {'asc'|'desc'} [params.sort='desc'] - Sort order by base card rating
 * @returns {Promise<Array>} Array of PlayerListItem objects
 */
export const getPlayers = async ({ search, in_club = 'all', sort = 'desc' } = {}) => {
  const params = {};
  if (search) params.search = search;
  if (in_club !== 'all') params.in_club = in_club;
  if (sort) params.sort = sort;

  const response = await apiClient.get('/players', { params });
  return response.data;
};

/**
 * Get detailed information about a specific player including all their cards.
 * 
 * @param {string} slug - Player slug identifier (e.g., "ronald-araujo")
 * @returns {Promise<Object>} PlayerDetail object
 */
export const getPlayer = async (slug) => {
  const response = await apiClient.get(`/players/${slug}`);
  return response.data;
};

/**
 * Update a card's in_club status.
 * 
 * @param {string} cardSlug - Card slug identifier (may contain slashes, will be URL-encoded)
 * @param {boolean} inClub - New in_club status
 * @returns {Promise<void>}
 */
export const updateCard = async (cardSlug, inClub) => {
  // URL-encode the card_slug to handle slashes
  const encodedSlug = encodeURIComponent(cardSlug);
  await apiClient.patch(`/cards/${encodedSlug}/club`, { in_club: inClub });
};

/**
 * Trigger a background scrape of the FUT.GG site.
 * 
 * @returns {Promise<Object>} Response with status and message
 */
export const triggerScrape = async () => {
  const response = await apiClient.post('/scrape');
  return response.data;
};

/**
 * Check if a scrape is currently in progress.
 * 
 * @returns {Promise<Object>} Object with in_progress boolean
 */
export const getScrapeStatus = async () => {
  const response = await apiClient.get('/scrape/status');
  return response.data;
};

export const getPlayerCounts = async () => {
  const response = await apiClient.get('/players/counts');
  return response.data;
};

// Export the axios instance in case it's needed directly
export default apiClient;