import React, { useState } from 'react';
import { api } from '../services/api';

export default function Login({ onLoginSuccess, onGoToRegister }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login(username, password);
      onLoginSuccess(data.user);
    } catch (err) {
      setError(err.message || 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (u, p) => {
    setUsername(u);
    setPassword(p);
    setError('');
    setLoading(true);
    try {
      const data = await api.login(u, p);
      onLoginSuccess(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '3.5rem 0', maxWidth: '440px' }}>
      <div style={{
        backgroundColor: '#131d2e',
        border: '1px solid #1e2f49',
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.4)'
      }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '0.4rem', textAlign: 'center' }}>
          Welcome Back
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1.5rem', textAlign: 'center' }}>
          Sign in to access your ratings, reviews, and graph recommendations.
        </p>

        {error && (
          <div style={{
            backgroundColor: '#450a0a',
            border: '1px solid #991b1b',
            color: '#fca5a5',
            padding: '0.65rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '1.25rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. demo_user"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={{ margin: '1.75rem 0', textAlign: 'center', position: 'relative' }}>
          <hr style={{ borderColor: '#1e2f49' }} />
          <span style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: '#131d2e',
            padding: '0 0.5rem',
            color: '#64748b',
            fontSize: '0.75rem'
          }}>
            ONE-CLICK DEMO LOGINS
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button
            type="button"
            className="btn-secondary"
            style={{ fontSize: '0.8rem', justifyContent: 'flex-start' }}
            onClick={() => handleQuickLogin('demo_user', 'demo123')}
          >
            🚀 Demo User (General tester)
          </button>
          <button
            type="button"
            className="btn-secondary"
            style={{ fontSize: '0.8rem', justifyContent: 'flex-start' }}
            onClick={() => handleQuickLogin('alex_reviewer', 'alex123')}
          >
            🌌 Alex (Sci-Fi & Nolan enthusiast)
          </button>
          <button
            type="button"
            className="btn-secondary"
            style={{ fontSize: '0.8rem', justifyContent: 'flex-start' }}
            onClick={() => handleQuickLogin('sarah_cinephile', 'sarah123')}
          >
            🎭 Sarah (Tarantino & Thrillers fan)
          </button>
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.85rem', color: '#94a3b8' }}>
          Don't have an account?{' '}
          <button
            onClick={onGoToRegister}
            style={{ background: 'none', border: 'none', color: '#60a5fa', cursor: 'pointer', fontWeight: 600 }}
          >
            Register here
          </button>
        </div>
      </div>
    </div>
  );
}

