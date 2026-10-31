import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Watchlist({ user, onSelectMovie, onBrowseMovies }) {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadWatchlist();
    }
  }, [user]);

  const loadWatchlist = async () => {
    setLoading(true);
    try {
      const data = await api.getWatchlist(user.id);
      setWatchlist(data.watchlist || []);
    } catch (err) {
      console.error('Failed to load watchlist', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (movieId) => {
    try {
      await api.removeFromWatchlist(user.id, movieId);
      setWatchlist(watchlist.filter((m) => m.id !== movieId));
    } catch (err) {
      alert('Error removing movie: ' + err.message);
    }
  };

  if (!user) {
    return (
      <div className="container watchlist-page">
        <div className="empty-state">
          <h3>Sign in to manage your Watchlist</h3>
          <p>Save movies you want to explore later and improve your recommendations.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container watchlist-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>My Watchlist</h1>
          <p style={{ color: '#94a3b8' }}>
            {watchlist.length} {watchlist.length === 1 ? 'movie' : 'movies'} queued for your next movie night
          </p>
        </div>
        <button className="btn-secondary" onClick={onBrowseMovies}>
          + Explore More Movies
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Loading your watchlist...
        </div>
      ) : watchlist.length === 0 ? (
        <div className="empty-state">
          <h3>Your watchlist is empty</h3>
          <p style={{ marginBottom: '1.5rem' }}>
            Browse the movie catalog and click "+ Add to Watchlist" to queue titles.
          </p>
          <button className="btn-primary" onClick={onBrowseMovies}>
            Browse Movies Catalog
          </button>
        </div>
      ) : (
        <div className="movie-grid">
          {watchlist.map((movie) => (
            <div key={movie.id} className="movie-card" onClick={() => onSelectMovie(movie.id)}>
              <div className="poster-wrap">
                <img
                  src={movie.poster}
                  alt={movie.title}
                  className="poster-img"
                  loading="lazy"
                />
                <div className="rating-badge">★ {movie.user_rating_avg || movie.rating}</div>
              </div>
              <div className="card-body">
                <h3 className="card-title">{movie.title}</h3>
                <div className="card-meta">
                  <span>{movie.year}</span> • <span>{movie.director}</span>
                </div>
                <div className="card-genres">
                  {(movie.genres || []).map((g) => (
                    <span key={g} className="card-genre-pill">{g}</span>
                  ))}
                </div>
                <div className="card-footer" onClick={(e) => e.stopPropagation()}>
                  <button
                    className="btn-danger"
                    style={{ width: '100%' }}
                    onClick={() => handleRemove(movie.id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

