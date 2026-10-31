import React from 'react';

export default function MovieCard({ movie, onSelect, onToggleWatchlist, inWatchlist }) {
  if (!movie) return null;

  return (
    <div className="movie-card" onClick={() => onSelect(movie.id)}>
      <div className="poster-wrap">
        <img
          src={movie.poster || 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80'}
          alt={movie.title}
          className="poster-img"
          loading="lazy"
          onError={(e) => {
            e.target.src = 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600&auto=format&fit=crop&q=80';
          }}
        />
        <div className="rating-badge">
          ★ {movie.user_rating_avg || movie.rating}
        </div>
      </div>

      <div className="card-body">
        <h3 className="card-title" title={movie.title}>{movie.title}</h3>
        <div className="card-meta">
          <span>{movie.year}</span> • <span>{movie.director}</span>
        </div>

        <div className="card-genres">
          {(movie.genres || []).slice(0, 3).map((g) => (
            <span key={g} className="card-genre-pill">{g}</span>
          ))}
        </div>

        <div className="card-footer" onClick={(e) => e.stopPropagation()}>
          <button
            className="btn-secondary"
            style={{ width: '100%', fontSize: '0.8rem', padding: '0.35rem 0.5rem' }}
            onClick={() => onToggleWatchlist(movie.id)}
          >
            {inWatchlist ? '✓ In Watchlist' : '+ Watchlist'}
          </button>
        </div>
      </div>
    </div>
  );
}

