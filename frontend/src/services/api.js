const API_BASE = '/api';

async function fetchJson(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || `HTTP error ${res.status}`);
    }
    return data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // System Status & Seed
  getStatus: () => fetchJson('/status'),
  seedDatabase: () => fetchJson('/seed', { method: 'POST' }),
  importTMDB: (offset = 0, limit = 100) => fetchJson('/tmdb/import', {
    method: 'POST',
    body: JSON.stringify({ limit, offset })
  }),
  getTMDBStatus: () => fetchJson('/tmdb/status'),
  syncToNeo4j: () => fetchJson('/neo4j/sync', { method: 'POST' }),
  getNeo4jStatus: () => fetchJson('/neo4j/status'),

  // Movies
  getMovies: (params = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.set('search', params.search);
    if (params.genre && params.genre !== 'All') query.set('genre', params.genre);
    if (params.sort) query.set('sort', params.sort);
    if (params.page) query.set('page', params.page);
    if (params.limit) query.set('limit', params.limit);
    return fetchJson(`/movies?${query.toString()}`);
  },

  getMovieDetails: (id) => fetchJson(`/movies/${id}`),
  getGenres: () => fetchJson('/genres'),
  getSimilarMovies: (id) => fetchJson(`/movies/${id}/similar`),

  // Recommendations
  getRecommendations: (userId = null) => {
    const url = userId ? `/recommendations?user_id=${userId}` : '/recommendations';
    return fetchJson(url);
  },

  // Auth
  login: (username, password) => fetchJson('/users/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),

  register: (userData) => fetchJson('/users/register', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),

  getUserProfile: (userId) => fetchJson(`/users/${userId}`),

  // Ratings
  rateMovie: (movieId, userId, username, rating) => fetchJson(`/movies/${movieId}/ratings`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, username, rating })
  }),

  getUserRating: (movieId, userId) => fetchJson(`/movies/${movieId}/user-rating/${userId}`),

  // Reviews
  getReviews: (movieId) => fetchJson(`/movies/${movieId}/reviews`),
  addReview: (movieId, reviewData) => fetchJson(`/movies/${movieId}/reviews`, {
    method: 'POST',
    body: JSON.stringify(reviewData)
  }),
  deleteReview: (reviewId) => fetchJson(`/reviews/${reviewId}`, { method: 'DELETE' }),

  // Watchlist
  getWatchlist: (userId) => fetchJson(`/watchlist/${userId}`),
  addToWatchlist: (userId, movieId) => fetchJson('/watchlist', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, movie_id: movieId })
  }),
  removeFromWatchlist: (userId, movieId) => fetchJson(`/watchlist/${userId}/${movieId}`, {
    method: 'DELETE'
  })
};

