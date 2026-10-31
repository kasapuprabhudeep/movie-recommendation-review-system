import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import RatingModal from '../components/RatingModal';
import ReviewModal from '../components/ReviewModal';
import RecommendationCard from '../components/RecommendationCard';

export default function MovieDetails({
  movieId,
  onBack,
  onSelectMovie,
  user,
  watchlistIds,
  onToggleWatchlist
}) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userRating, setUserRating] = useState(null);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);

  useEffect(() => {
    loadMovieDetails();
    if (user) {
      loadUserRating();
    }
  }, [movieId, user]);

  const loadMovieDetails = async () => {
    setLoading(true);
    try {
      const data = await api.getMovieDetails(movieId);
      setDetails(data);
    } catch (err) {
      console.error('Failed to load movie details', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUserRating = async () => {
    try {
      const res = await api.getUserRating(movieId, user.id);
      if (res.rated) {
        setUserRating(res.rating);
      } else {
        setUserRating(null);
      }
    } catch (err) {
      console.error('Failed to load user rating', err);
    }
  };

  const handleRateSubmit = async (ratingVal) => {
    if (!user) {
      alert('Please log in to rate movies.');
      return;
    }
    try {
      await api.rateMovie(movieId, user.id, user.username, ratingVal);
      setUserRating(ratingVal);
      setShowRatingModal(false);
      loadMovieDetails();
    } catch (err) {
      alert('Error submitting rating: ' + err.message);
    }
  };

  const handleReviewSubmit = async (reviewData) => {
    if (!user) {
      alert('Please log in to submit a review.');
      return;
    }
    try {
      await api.addReview(movieId, {
        user_id: user.id,
        username: user.username,
        ...reviewData
      });
      setShowReviewModal(false);
      loadMovieDetails();
    } catch (err) {
      alert('Error submitting review: ' + err.message);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    try {
      await api.deleteReview(reviewId);
      loadMovieDetails();
    } catch (err) {
      alert('Error deleting review: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '4rem 0', textAlign: 'center', color: '#94a3b8' }}>
        Loading movie details...
      </div>
    );
  }

  if (!details || !details.movie) {
    return (
      <div className="container" style={{ padding: '4rem 0', textAlign: 'center' }}>
        <h2>Movie not found</h2>
        <button className="btn-secondary" onClick={onBack} style={{ marginTop: '1rem' }}>
          ← Back to Movies
        </button>
      </div>
    );
  }

  const { movie, reviews = [], similar = [] } = details;
  const inWatchlist = watchlistIds.includes(movie.id);

  return (
    <div className="container details-page">
      <div className="back-link" onClick={onBack}>
        ← Back to Movies
      </div>

      <div className="details-grid">
        <div className="details-poster-wrap">
          <img src={movie.poster} alt={movie.title} className="details-poster" />
        </div>

        <div className="details-info">
          <h1>{movie.title}</h1>

          <div className="details-meta-row">
            <span>📅 {movie.year}</span>
            <span>⏱️ {movie.runtime || '120 min'}</span>
            <span>🎬 Directed by <strong>{movie.director}</strong></span>
          </div>

          <div className="card-genres" style={{ marginBottom: '1.25rem' }}>
            {(movie.genres || []).map((g) => (
              <span key={g} className="card-genre-pill" style={{ fontSize: '0.8rem', padding: '0.2rem 0.6rem' }}>
                {g}
              </span>
            ))}
          </div>

          <div className="details-rating-box">
            <span>★ {movie.user_rating_avg || movie.rating} / 10</span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 400 }}>
              ({movie.user_rating_count ? `${movie.user_rating_count} community ratings` : `${movie.votes?.toLocaleString() || 0} IMDb votes`})
            </span>
          </div>

          {userRating && (
            <div style={{ color: '#4ade80', fontSize: '0.9rem', marginBottom: '1rem', fontWeight: 600 }}>
              ✓ You rated this movie {userRating} / 5 stars
            </div>
          )}

          <div className="details-actions">
            <button
              className="btn-primary"
              onClick={() => onToggleWatchlist(movie.id)}
            >
              {inWatchlist ? '✓ In Watchlist' : '+ Add to Watchlist'}
            </button>

            <button
              className="btn-secondary"
              onClick={() => setShowRatingModal(true)}
            >
              ★ {userRating ? 'Update Rating' : 'Rate Movie'}
            </button>

            <button
              className="btn-secondary"
              onClick={() => setShowReviewModal(true)}
            >
              ✎ Write Review
            </button>
          </div>

          <p className="details-plot">{movie.plot}</p>

          <div className="details-crew">
            <div className="crew-item">
              <span className="crew-label">Director:</span>
              <span>{movie.director}</span>
            </div>
            <div className="crew-item">
              <span className="crew-label">Starring:</span>
              <span>{(movie.actors || []).join(', ')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Graph Similar Movies */}
      <section style={{ marginBottom: '3.5rem' }}>
        <h2 className="section-title">
          <span>Graph-Traversed Similar Movies</span>
          <span style={{ fontSize: '0.85rem', color: '#60a5fa', fontWeight: 500 }}>
            Neo4j / Graph Path Matching
          </span>
        </h2>

        {similar.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No similar graph paths found.</p>
        ) : (
          <div className="movie-grid">
            {similar.map((rec) => (
              <RecommendationCard
                key={rec.movie.id}
                recommendation={rec}
                onSelect={onSelectMovie}
                onToggleWatchlist={onToggleWatchlist}
                inWatchlist={watchlistIds.includes(rec.movie.id)}
              />
            ))}
          </div>
        )}
      </section>

      {/* Reviews Section */}
      <section>
        <div className="section-title">
          <span>Community Reviews ({reviews.length})</span>
          <button className="btn-secondary" onClick={() => setShowReviewModal(true)} style={{ fontSize: '0.85rem' }}>
            + Add Review
          </button>
        </div>

        {reviews.length === 0 ? (
          <div className="empty-state">
            <h3>No reviews yet</h3>
            <p>Be the first film enthusiast to review {movie.title}!</p>
          </div>
        ) : (
          <div className="review-list">
            {reviews.map((r) => (
              <div key={r.id || r._id} className="review-card">
                <div className="review-header">
                  <div>
                    <span className="review-author">@{r.username}</span>
                    <span style={{ margin: '0 0.5rem', color: '#475569' }}>•</span>
                    <span style={{ color: '#fbbf24', fontWeight: 600 }}>★ {r.rating} / 5</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span className="review-date">
                      {r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}
                    </span>
                    {user && (user.id === r.user_id || user.username === r.username) && (
                      <button
                        className="btn-danger"
                        onClick={() => handleDeleteReview(r.id || r._id)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
                <h4 className="review-title">{r.title}</h4>
                <p className="review-content">{r.content}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Modals */}
      {showRatingModal && (
        <RatingModal
          movie={movie}
          currentRating={userRating}
          onClose={() => setShowRatingModal(false)}
          onSubmit={handleRateSubmit}
        />
      )}

      {showReviewModal && (
        <ReviewModal
          movie={movie}
          onClose={() => setShowReviewModal(false)}
          onSubmit={handleReviewSubmit}
        />
      )}
    </div>
  );
}

