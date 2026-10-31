import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import RecommendationCard from '../components/RecommendationCard';

const DEMO_PERSONAS = [
  { id: 'u1', name: 'Alex Johnson', desc: 'Sci-Fi & Nolan Fan' },
  { id: 'u2', name: 'Sarah Miller', desc: 'Tarantino & Thrillers' },
  { id: 'u3', name: 'David Chen', desc: 'Cyberpunk & 90s Classics' },
  { id: 'u4', name: 'Demo User', desc: 'Active Test Account' }
];

export default function Recommendations({
  currentUser,
  onSelectMovie,
  watchlistIds,
  onToggleWatchlist
}) {
  const [selectedUserId, setSelectedUserId] = useState(currentUser?.id || 'u1');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (currentUser) {
      setSelectedUserId(currentUser.id);
    }
  }, [currentUser]);

  useEffect(() => {
    loadRecommendations(selectedUserId);
  }, [selectedUserId]);

  const loadRecommendations = async (uid) => {
    setLoading(true);
    try {
      const data = await api.getRecommendations(uid);
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error('Failed to load recommendations', err);
    } finally {
      setLoading(false);
    }
  };

  const currentPersona = DEMO_PERSONAS.find((p) => p.id === selectedUserId);

  return (
    <div className="container" style={{ padding: '2.5rem 0' }}>
      <section style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          Graph-Powered Recommendations
        </h1>
        <p style={{ color: '#94a3b8', maxWidth: '700px', margin: '0 auto' }}>
          Recommendations generated through multi-hop graph traversals: combining shared genres,
          directors, actors, user ratings, and collaborative filtering.
        </p>
      </section>

      {/* Persona Switcher to Demonstrate Dynamic Graph Changes */}
      <div className="user-switch-bar">
        <div>
          <span className="user-switch-label">Simulate Recommendations for User Persona:</span>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.2rem' }}>
            Current: <strong>{currentPersona ? `${currentPersona.name} (${currentPersona.desc})` : (currentUser?.name || 'Guest')}</strong>
          </div>
        </div>

        <div className="user-switch-pills">
          {DEMO_PERSONAS.map((p) => (
            <button
              key={p.id}
              className={`user-pill ${selectedUserId === p.id ? 'active' : ''}`}
              onClick={() => setSelectedUserId(p.id)}
            >
              {p.name.split(' ')[0]} ({p.desc})
            </button>
          ))}
          <button
            className={`user-pill ${!selectedUserId ? 'active' : ''}`}
            onClick={() => setSelectedUserId(null)}
          >
            General Trending
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
          Traversing graph relationships and computing similarity scores...
        </div>
      ) : recommendations.length === 0 ? (
        <div className="empty-state">
          <h3>No recommendations available yet</h3>
          <p>Rate more movies to let the graph engine learn your unique taste!</p>
        </div>
      ) : (
        <div className="movie-grid">
          {recommendations.map((rec) => (
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
    </div>
  );
}

