import React from 'react';

export default function RecommendationCard({ recommendation, onSelect, onToggleWatchlist, inWatchlist }) {
  const { movie, explanation, score } = recommendation;
  if (!movie) return null;

  return (
    <div className="rec-card" onClick={() => onSelect(movie.id)} style={{ cursor: 'pointer' }}>
      <div className="rec-explanation-banner">
        <span>⚡ <strong>Why Recommended:</strong> {explanation}</span>
        {score && <span className="rec-score-badge">Score: {score}</span>}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <div className="poster-wrap" style={{ height: '260px' }}>
          <img
            src={movie.poster || 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80'}
            alt={movie.title}
            className="poster-img"
            loading="lazy"
          />
          <div className="rating-badge">
            ★ {movie.user_rating_avg || movie.rating}
          </div>
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
              className="btn-secondary"
              style={{ width: '100%', fontSize: '0.8rem', padding: '0.35rem 0.5rem' }}
              onClick={() => onToggleWatchlist(movie.id)}
            >
              {inWatchlist ? '✓ In Watchlist' : '+ Watchlist'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

