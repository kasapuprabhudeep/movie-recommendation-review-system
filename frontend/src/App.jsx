import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import StatusBanner from './components/StatusBanner';
import Home from './pages/Home';
import MovieDetails from './pages/MovieDetails';
import Recommendations from './pages/Recommendations';
import Watchlist from './pages/Watchlist';
import Login from './pages/Login';
import Register from './pages/Register';
import { api } from './services/api';

export default function App() {
  const [currentView, setView] = useState('home');
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [watchlistIds, setWatchlistIds] = useState([]);
  
  // Load saved user or default to demo user for a seamless out-of-the-box demo
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('cinerec_user');
      return saved ? JSON.parse(saved) : { id: 'u4', username: 'demo_user', name: 'Demo User' };
    } catch {
      return { id: 'u4', username: 'demo_user', name: 'Demo User' };
    }
  });

  useEffect(() => {
    loadSystemStatus();
  }, []);

  useEffect(() => {
    if (user?.id) {
      loadWatchlist();
    } else {
      setWatchlistIds([]);
    }
  }, [user]);

  const loadSystemStatus = async () => {
    try {
      const status = await api.getStatus();
      setSystemStatus(status);
    } catch (err) {
      console.error('Failed to load system status', err);
    }
  };

  const loadWatchlist = async () => {
    try {
      const data = await api.getWatchlist(user.id);
      const ids = (data.watchlist || []).map((m) => m.id);
      setWatchlistIds(ids);
    } catch (err) {
      console.error('Failed to load watchlist', err);
    }
  };

  const handleToggleWatchlist = async (movieId) => {
    if (!user) {
      alert('Please log in to manage your watchlist.');
      setView('login');
      return;
    }

    const isPresent = watchlistIds.includes(movieId);
    try {
      if (isPresent) {
        await api.removeFromWatchlist(user.id, movieId);
        setWatchlistIds(watchlistIds.filter((id) => id !== movieId));
      } else {
        await api.addToWatchlist(user.id, movieId);
        setWatchlistIds([...watchlistIds, movieId]);
      }
      loadSystemStatus();
    } catch (err) {
      alert('Error updating watchlist: ' + err.message);
    }
  };

  const handleSelectMovie = (id) => {
    setSelectedMovieId(id);
    setView('movie_details');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('cinerec_user', JSON.stringify(userData));
    setView('home');
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('cinerec_user');
    setWatchlistIds([]);
    setView('home');
  };

  const handleSeedDatabase = async () => {
    if (!window.confirm('Reset database to initial sample dataset with 15 movies and graph relationships?')) {
      return;
    }
    try {
      const res = await api.seedDatabase();
      alert('Database successfully reset and re-seeded!');
      loadSystemStatus();
      if (user) loadWatchlist();
      setView('home');
    } catch (err) {
      alert('Failed to reset database: ' + err.message);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        currentView={currentView}
        setView={setView}
        user={user}
        onLogout={handleLogout}
        onSeed={handleSeedDatabase}
        systemStatus={systemStatus}
      />

      <StatusBanner status={systemStatus} onRefreshStatus={loadSystemStatus} />

      <main style={{ flex: 1 }}>
        {currentView === 'home' && (
          <Home
            onSelectMovie={handleSelectMovie}
            watchlistIds={watchlistIds}
            onToggleWatchlist={handleToggleWatchlist}
          />
        )}

        {currentView === 'movie_details' && (
          <MovieDetails
            movieId={selectedMovieId}
            onBack={() => setView('home')}
            onSelectMovie={handleSelectMovie}
            user={user}
            watchlistIds={watchlistIds}
            onToggleWatchlist={handleToggleWatchlist}
          />
        )}

        {currentView === 'recommendations' && (
          <Recommendations
            currentUser={user}
            onSelectMovie={handleSelectMovie}
            watchlistIds={watchlistIds}
            onToggleWatchlist={handleToggleWatchlist}
          />
        )}

        {currentView === 'watchlist' && (
          <Watchlist
            user={user}
            onSelectMovie={handleSelectMovie}
            onBrowseMovies={() => setView('home')}
          />
        )}

        {currentView === 'login' && (
          <Login
            onLoginSuccess={handleLoginSuccess}
            onGoToRegister={() => setView('register')}
          />
        )}

        {currentView === 'register' && (
          <Register
            onRegisterSuccess={handleLoginSuccess}
            onGoToLogin={() => setView('login')}
          />
        )}
      </main>

      <footer style={{
        backgroundColor: '#0c121f',
        borderTop: '1px solid #1e293b',
        padding: '1.5rem 0',
        textAlign: 'center',
        color: '#64748b',
        fontSize: '0.85rem'
      }}>
        <div className="container">
          <p>
            CineGraph — Movie Recommendation & Review System • Built with React, Python Flask, MongoDB & Neo4j
          </p>
          <p style={{ marginTop: '0.35rem', color: '#475569' }}>
            Graph Traversal • Collaborative Filtering • Explainable AI
          </p>
        </div>
      </footer>
    </div>
  );
}

