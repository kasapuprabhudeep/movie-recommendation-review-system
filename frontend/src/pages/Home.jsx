import React, { useState, useEffect, useCallback } from 'react';
import MovieCard from '../components/MovieCard';
import { api } from '../services/api';

const PAGE_SIZE = 24; // cards per page

export default function Home({ onSelectMovie, watchlistIds, onToggleWatchlist }) {
  const [movies, setMovies] = useState([]);
  const [totalMovies, setTotalMovies] = useState(0);
  const [genres, setGenres] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('All');
  const [sortBy, setSortBy] = useState('rating');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // TMDB panel state
  const [showTMDB, setShowTMDB] = useState(false);
  const [tmdbStatus, setTmdbStatus] = useState(null);
  const [tmdbOffset, setTmdbOffset] = useState(0);
  const [tmdbLoading, setTmdbLoading] = useState(false);
  const [tmdbMessage, setTmdbMessage] = useState('');

  useEffect(() => { loadGenres(); loadTMDBStatus(); }, []);
  useEffect(() => { setPage(1); }, [search, selectedGenre, sortBy]);
  useEffect(() => { loadMovies(); }, [search, selectedGenre, sortBy, page]);

  const loadGenres = async () => {
    try {
      const data = await api.getGenres();
      setGenres(['All', ...data.genres]);
    } catch (e) { console.error(e); }
  };

  const loadTMDBStatus = async () => {
    try {
      const s = await api.getTMDBStatus();
      setTmdbStatus(s);
      setTmdbOffset(s.total_in_db > 15 ? s.total_in_db - 15 : 0);
    } catch (e) { /* backend offline */ }
  };

  const loadMovies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMovies({
        search,
        genre: selectedGenre,
        sort: sortBy,
        page,
        limit: PAGE_SIZE
      });
      setMovies(data.movies || []);
      setTotalMovies(data.total || 0);
    } catch (e) {
      setError('Cannot reach Flask backend on port 5000. Please run start_backend.bat first.');
    } finally {
      setLoading(false);
    }
  }, [search, selectedGenre, sortBy, page]);

  const handleImportNext = async () => {
    setTmdbLoading(true);
    setTmdbMessage('');
    try {
      const res = await api.importTMDB(tmdbOffset, 100);
      if (res.success) {
        setTmdbMessage(`✅ Imported ${res.imported_count} movies (rows ${res.offset_used}–${res.next_offset}). Total in DB: ${res.total_in_db}. ${res.has_more ? 'More available!' : 'All CSV rows processed!'}`);
        setTmdbOffset(res.next_offset);
        await loadGenres();
        await loadMovies();
        await loadTMDBStatus();
      } else {
        setTmdbMessage(`❌ ${res.error}`);
      }
    } catch (e) {
      setTmdbMessage(`❌ Import failed: ${e.message}`);
    } finally {
      setTmdbLoading(false);
    }
  };

  const handleSeedReset = async () => {
    if (!window.confirm('Reset to the 15 sample movies? TMDB imports will be cleared.')) return;
    try {
      await api.seedDatabase();
      setTmdbOffset(0);
      await loadGenres();
      await loadMovies();
      await loadTMDBStatus();
      alert('Reset complete — 15 sample movies loaded.');
    } catch (e) { alert('Error: ' + e.message); }
  };

  const totalPages = Math.ceil(totalMovies / PAGE_SIZE);

  return (
    <div className="container">
      {/* Hero */}
      <section className="hero">
        <h1>Explore &amp; Discover Cinema</h1>
        <p>
          MongoDB stores your movie library · Neo4j graph engine drives recommendations · TMDB dataset support for 5,000+ films
        </p>
      </section>

      {/* Backend error */}
      {error && (
        <div style={{ background:'#450a0a', border:'1px solid #b91c1c', color:'#fecaca', borderRadius:'10px', padding:'1.25rem', marginBottom:'1.5rem', textAlign:'center' }}>
          <h3 style={{ color:'#fff', marginBottom:'0.4rem' }}>⚡ Backend Not Running</h3>
          <p style={{ marginBottom:'1rem' }}>{error}</p>
          <button className="btn-primary" onClick={loadMovies}>↻ Retry</button>
        </div>
      )}

      {/* TMDB Import Manager */}
      <div style={{ marginBottom:'1.5rem' }}>
        <button
          className="btn-secondary"
          style={{ width:'100%', justifyContent:'space-between', padding:'0.75rem 1rem' }}
          onClick={() => setShowTMDB(!showTMDB)}
        >
          <span>📥 TMDB Dataset Manager — {totalMovies} movies in database</span>
          <span>{showTMDB ? '▲ Hide' : '▼ Show'}</span>
        </button>

        {showTMDB && (
          <div style={{ background:'#0d1527', border:'1px solid #1e3a5f', borderRadius:'0 0 10px 10px', padding:'1.25rem' }}>
            {tmdbStatus ? (
              tmdbStatus.movies_csv_found ? (
                <div>
                  <div style={{ display:'flex', flexWrap:'wrap', gap:'1rem', marginBottom:'1rem', fontSize:'0.85rem', color:'#94a3b8' }}>
                    <span>📄 CSV rows: <strong style={{color:'#f8fafc'}}>{tmdbStatus.total_csv_rows.toLocaleString()}</strong></span>
                    <span>🎬 In database: <strong style={{color:'#4ade80'}}>{totalMovies}</strong></span>
                    <span>📌 Next batch starts at row: <strong style={{color:'#93c5fd'}}>{tmdbOffset}</strong></span>
                    <span>✅ Credits file: <strong style={{color: tmdbStatus.credits_csv_found ? '#4ade80':'#f87171'}}>{tmdbStatus.credits_csv_found ? 'Found (Directors & Cast)' : 'Not found – drop credits CSV for cast data'}</strong></span>
                  </div>

                  <div style={{ display:'flex', gap:'0.75rem', flexWrap:'wrap', alignItems:'center' }}>
                    <button
                      className="btn-primary"
                      onClick={handleImportNext}
                      disabled={tmdbLoading || tmdbOffset >= tmdbStatus.total_csv_rows}
                      style={{ minWidth:'200px' }}
                    >
                      {tmdbLoading ? 'Importing...' : tmdbOffset >= tmdbStatus.total_csv_rows ? '✅ All movies imported' : `📥 Import Next 100 (row ${tmdbOffset}→${Math.min(tmdbOffset+100, tmdbStatus.total_csv_rows)})`}
                    </button>

                    <button
                      className="btn-secondary"
                      onClick={() => { setTmdbOffset(0); setTmdbMessage('Offset reset to start of CSV.'); }}
                      disabled={tmdbLoading}
                    >
                      ↺ Restart from Row 0
                    </button>

                    <button className="btn-danger" onClick={handleSeedReset} disabled={tmdbLoading}>
                      🗑 Reset to 15 Sample Movies
                    </button>
                  </div>

                  {/* Progress bar */}
                  {tmdbStatus.total_csv_rows > 0 && (
                    <div style={{ marginTop:'1rem' }}>
                      <div style={{ display:'flex', justifyContent:'space-between', fontSize:'0.75rem', color:'#64748b', marginBottom:'0.35rem' }}>
                        <span>Import progress</span>
                        <span>{Math.round((tmdbOffset / tmdbStatus.total_csv_rows) * 100)}% of {tmdbStatus.total_csv_rows} CSV rows processed</span>
                      </div>
                      <div style={{ background:'#1e293b', borderRadius:'999px', height:'8px', overflow:'hidden' }}>
                        <div style={{ background:'linear-gradient(90deg, #2563eb, #60a5fa)', width:`${Math.min(100, (tmdbOffset / tmdbStatus.total_csv_rows) * 100)}%`, height:'100%', borderRadius:'999px', transition:'width 0.4s ease' }} />
                      </div>
                    </div>
                  )}

                  {tmdbMessage && (
                    <p style={{ marginTop:'0.85rem', color:'#93c5fd', fontSize:'0.85rem', background:'#0b1120', padding:'0.5rem 0.75rem', borderRadius:'6px', border:'1px solid #1e3a5f' }}>
                      {tmdbMessage}
                    </p>
                  )}
                </div>
              ) : (
                <div style={{ color:'#fbbf24' }}>
                  <p style={{ marginBottom:'0.5rem' }}>⚠️ TMDB CSV not found. Drop your files here:</p>
                  <code style={{ background:'#0b1120', padding:'0.5rem 0.75rem', borderRadius:'6px', display:'block', color:'#93c5fd', fontSize:'0.85rem' }}>
                    {tmdbStatus.tmdb_dir}
                  </code>
                  <p style={{ marginTop:'0.5rem', fontSize:'0.82rem', color:'#94a3b8' }}>
                    Download from <strong>kaggle.com/datasets/tmdb/tmdb-movie-metadata</strong> → place <strong>tmdb_5000_movies.csv</strong> (and optionally <strong>tmdb_5000_credits.csv</strong>) into the folder above.
                  </p>
                </div>
              )
            ) : (
              <p style={{ color:'#94a3b8' }}>Loading TMDB status...</p>
            )}
          </div>
        )}
      </div>

      {/* Search + Filter Toolbar */}
      <div className="toolbar">
        <div className="search-row">
          <div className="search-input-wrap">
            <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              className="search-input"
              placeholder="Search title, director, actor, plot..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <select className="sort-select" value={sortBy} onChange={e => setSortBy(e.target.value)}>
            <option value="rating">Highest Rated</option>
            <option value="year">Newest First</option>
            <option value="title">Title (A-Z)</option>
          </select>
        </div>
        <div className="genre-chips">
          {genres.map(g => (
            <button key={g} className={`chip ${selectedGenre === g ? 'active' : ''}`} onClick={() => setSelectedGenre(g)}>{g}</button>
          ))}
        </div>
      </div>

      {/* Count + pagination info */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.25rem', flexWrap:'wrap', gap:'0.5rem' }}>
        <h2 style={{ fontSize:'1.1rem', fontWeight:700 }}>
          {selectedGenre === 'All' ? 'All Movies' : `${selectedGenre} Films`}
          <span style={{ marginLeft:'0.5rem', color:'#60a5fa' }}>({totalMovies} total)</span>
        </h2>
        {totalPages > 1 && (
          <span style={{ fontSize:'0.85rem', color:'#94a3b8' }}>
            Page {page} of {totalPages} ({PAGE_SIZE} per page)
          </span>
        )}
      </div>

      {/* Movie Grid */}
      {loading ? (
        <div style={{ textAlign:'center', padding:'3rem', color:'#94a3b8' }}>Loading movie library...</div>
      ) : movies.length === 0 ? (
        <div className="empty-state">
          <h3>No movies found</h3>
          <p style={{ marginBottom:'1rem' }}>Try a different search or genre filter.</p>
          <button className="btn-primary" onClick={handleSeedReset}>Load Sample Movies</button>
        </div>
      ) : (
        <div className="movie-grid">
          {movies.map(m => (
            <MovieCard
              key={m.id}
              movie={m}
              onSelect={onSelectMovie}
              onToggleWatchlist={onToggleWatchlist}
              inWatchlist={watchlistIds.includes(m.id)}
            />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && !loading && (
        <div style={{ display:'flex', justifyContent:'center', alignItems:'center', gap:'0.5rem', margin:'2.5rem 0', flexWrap:'wrap' }}>
          <button className="btn-secondary" onClick={() => setPage(1)} disabled={page === 1}>«</button>
          <button className="btn-secondary" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>‹ Prev</button>

          {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
            let pageNum;
            if (totalPages <= 7) {
              pageNum = i + 1;
            } else if (page <= 4) {
              pageNum = i + 1;
              if (i === 6) pageNum = totalPages;
            } else if (page >= totalPages - 3) {
              pageNum = totalPages - 6 + i;
            } else {
              const offsets = [-3, -2, -1, 0, 1, 2, 3];
              pageNum = page + offsets[i];
            }
            return (
              <button
                key={pageNum}
                className={page === pageNum ? 'btn-primary' : 'btn-secondary'}
                onClick={() => setPage(pageNum)}
                style={{ minWidth:'40px' }}
              >
                {pageNum}
              </button>
            );
          })}

          <button className="btn-secondary" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next ›</button>
          <button className="btn-secondary" onClick={() => setPage(totalPages)} disabled={page === totalPages}>»</button>
        </div>
      )}
    </div>
  );
}
