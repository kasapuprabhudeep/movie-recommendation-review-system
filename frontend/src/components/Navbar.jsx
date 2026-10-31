import React from 'react';

export default function Navbar({ currentView, setView, user, onLogout, onSeed, systemStatus }) {
  return (
    <nav className="navbar">
      <div className="container nav-container">
        <div className="nav-brand" onClick={() => setView('home')}>
          <svg viewBox="0 0 24 24">
            <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
          </svg>
          <span>CineGraph</span>
        </div>

        <ul className="nav-links">
          <li>
            <button
              className={`nav-btn ${currentView === 'home' ? 'active' : ''}`}
              onClick={() => setView('home')}
            >
              Movies
            </button>
          </li>
          <li>
            <button
              className={`nav-btn ${currentView === 'recommendations' ? 'active' : ''}`}
              onClick={() => setView('recommendations')}
            >
              Recommendations & Graph
            </button>
          </li>
          {user && (
            <li>
              <button
                className={`nav-btn ${currentView === 'watchlist' ? 'active' : ''}`}
                onClick={() => setView('watchlist')}
              >
                My Watchlist
              </button>
            </li>
          )}
        </ul>

        <div className="nav-user">
          {systemStatus && (
            <div className="badge-status" title={`MongoDB: ${systemStatus.mongodb?.mode} | Neo4j: ${systemStatus.neo4j?.mode}`}>
              <span className="badge-dot"></span>
              <span>{systemStatus.neo4j?.connected ? 'Neo4j Live' : 'Graph Engine Active'}</span>
            </div>
          )}

          <button
            className="btn-secondary"
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}
            onClick={onSeed}
            title="Reset database with sample data"
          >
            ↻ Reset Data
          </button>

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '0.85rem', color: '#93c5fd', fontWeight: 600 }}>
                {user.name || user.username}
              </span>
              <button className="btn-secondary" onClick={onLogout} style={{ fontSize: '0.8rem' }}>
                Logout
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn-secondary" onClick={() => setView('login')} style={{ fontSize: '0.85rem' }}>
                Login
              </button>
              <button className="btn-primary" onClick={() => setView('register')} style={{ fontSize: '0.85rem' }}>
                Register
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

