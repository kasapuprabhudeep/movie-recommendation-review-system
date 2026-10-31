import React, { useState } from 'react';
import { api } from '../services/api';

export default function Register({ onRegisterSuccess, onGoToLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    name: '',
    email: '',
    bio: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.register(formData);
      onRegisterSuccess(data.user);
    } catch (err) {
      setError(err.message || 'Registration failed');
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
          Create an Account
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1.5rem', textAlign: 'center' }}>
          Join the community to unlock personalized graph recommendations.
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
            <label className="form-label">Username *</label>
            <input
              type="text"
              name="username"
              className="form-input"
              value={formData.username}
              onChange={handleChange}
              placeholder="e.g. cinelover99"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              name="name"
              className="form-input"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. Jordan Lee"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              className="form-input"
              value={formData.email}
              onChange={handleChange}
              placeholder="e.g. jordan@example.com"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password *</label>
            <input
              type="password"
              name="password"
              className="form-input"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Bio (Favorite Genres / Movies)</label>
            <textarea
              name="bio"
              className="form-textarea"
              rows="2"
              value={formData.bio}
              onChange={handleChange}
              placeholder="e.g. Sci-Fi enthusiast, Nolan fan"
            ></textarea>
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: '#94a3b8' }}>
          Already have an account?{' '}
          <button
            onClick={onGoToLogin}
            style={{ background: 'none', border: 'none', color: '#60a5fa', cursor: 'pointer', fontWeight: 600 }}
          >
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}

