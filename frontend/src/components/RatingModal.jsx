import React, { useState } from 'react';

export default function RatingModal({ movie, currentRating, onClose, onSubmit }) {
  const [rating, setRating] = useState(currentRating || 5);
  const [hovered, setHovered] = useState(0);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(rating);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">Rate "{movie.title}"</h3>
        <p style={{ color: '#94a3b8', marginBottom: '1.25rem', fontSize: '0.9rem' }}>
          Your rating updates the graph recommendation engine for you and the community.
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', justifyContent: 'center', margin: '1.5rem 0' }}>
            <div className="star-rating-row">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  className={`star-btn ${(hovered || rating) >= star ? 'active' : ''}`}
                  onMouseEnter={() => setHovered(star)}
                  onMouseLeave={() => setHovered(0)}
                  onClick={() => setRating(star)}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <div style={{ textAlign: 'center', marginBottom: '1.5rem', fontWeight: 700, fontSize: '1.1rem', color: '#fbbf24' }}>
            {rating} / 5 Stars
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save Rating
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

