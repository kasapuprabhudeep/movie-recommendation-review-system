import React, { useState } from 'react';

export default function ReviewModal({ movie, onClose, onSubmit }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [rating, setRating] = useState(5);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!content.trim()) return;
    onSubmit({ title, content, rating });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">Write a Review for "{movie.title}"</h3>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Rating</label>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  className={`star-btn ${rating >= star ? 'active' : ''}`}
                  onClick={() => setRating(star)}
                  style={{ fontSize: '1.5rem' }}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Review Headline</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Masterful storytelling and cinematography"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Review Details</label>
            <textarea
              className="form-textarea"
              rows="4"
              placeholder="What did you think of the direction, actors, and plot?"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
            ></textarea>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Publish Review
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

