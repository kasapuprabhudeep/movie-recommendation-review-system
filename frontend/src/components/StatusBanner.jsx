import React, { useState } from 'react';
import { api } from '../services/api';

export default function StatusBanner({ status, onRefreshStatus }) {
  const [expanded, setExpanded] = useState(false);
  const [showNeo4jGuide, setShowNeo4jGuide] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState('');

  if (!status) return null;

  const mongoLive = status.mongodb?.connected;
  const neo4jLive = status.neo4j?.connected;

  const handleSyncToNeo4j = async () => {
    setSyncing(true);
    setSyncResult('');
    try {
      const res = await api.syncToNeo4j();
      if (res.success) {
        setSyncResult(`✅ ${res.message}`);
        if (onRefreshStatus) onRefreshStatus();
      } else {
        setSyncResult(`❌ ${res.error || 'Failed to sync'}`);
      }
    } catch (err) {
      setSyncResult(`❌ Error connecting to Neo4j: ${err.message}. Make sure your Neo4j DBMS is running and password matches.`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div style={{ backgroundColor:'#0d1527', borderBottom:'1px solid #1e2f49', fontSize:'0.82rem', color:'#94a3b8' }}>
      <div className="container" style={{ padding:'0.55rem 1.5rem', display:'flex', alignItems:'center', justifyContent:'space-between', flexWrap:'wrap', gap:'0.75rem' }}>
        <div style={{ display:'flex', alignItems:'center', gap:'1.5rem', flexWrap:'wrap' }}>
          {/* MongoDB */}
          <span style={{ display:'inline-flex', alignItems:'center', gap:'0.35rem' }}>
            <span style={{ color: mongoLive ? '#4ade80':'#fbbf24', fontSize:'0.9rem' }}>●</span>
            <strong>MongoDB:</strong>
            <span style={{ color: mongoLive ? '#4ade80':'#fbbf24' }}>
              {mongoLive ? 'Live Connected' : 'Embedded Engine'}
            </span>
          </span>

          {/* Neo4j */}
          <span
            style={{ display:'inline-flex', alignItems:'center', gap:'0.35rem', cursor:'pointer' }}
            onClick={() => setShowNeo4jGuide(!showNeo4jGuide)}
            title="Click to view Neo4j controls & setup guide"
          >
            <span style={{ color: neo4jLive ? '#4ade80':'#f59e0b', fontSize:'0.9rem' }}>●</span>
            <strong>Neo4j:</strong>
            <span style={{ color: neo4jLive ? '#4ade80':'#f59e0b', textDecoration:'underline dotted', textUnderlineOffset:'3px' }}>
              {neo4jLive ? `Live Connected (${status.neo4j?.live_nodes || 0} nodes)` : 'Click to connect Neo4j Desktop ▾'}
            </span>
          </span>

          {/* Sync Button directly in the bar */}
          <button
            className="btn-primary"
            style={{ fontSize:'0.75rem', padding:'0.25rem 0.65rem', background: neo4jLive ? '#166534':'#2563eb' }}
            onClick={handleSyncToNeo4j}
            disabled={syncing}
            title="Sync all movies, genres, actors, directors to Neo4j graph"
          >
            {syncing ? '🔄 Syncing Graph...' : neo4jLive ? '🔄 Sync Data to Neo4j' : '⚡ Connect & Sync to Neo4j'}
          </button>

          {/* Counts */}
          <span>🎬 <strong>{status.data_summary?.movies}</strong> movies</span>
          <span>🕸 <strong>{status.data_summary?.graph_nodes}</strong> nodes · <strong>{status.data_summary?.graph_relationships}</strong> edges</span>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          style={{ background:'none', border:'none', color:'#60a5fa', cursor:'pointer', fontSize:'0.78rem' }}
        >
          {expanded ? '▲ Hide Architecture' : '▼ Architecture Details'}
        </button>
      </div>

      {syncResult && (
        <div className="container" style={{ padding:'0.25rem 1.5rem 0.5rem' }}>
          <div style={{ background:'#0b1120', border:'1px solid #1e3a5f', borderRadius:'6px', padding:'0.5rem 0.85rem', color:'#93c5fd', fontSize:'0.82rem' }}>
            {syncResult}
          </div>
        </div>
      )}

      {/* Neo4j Desktop Setup Guide & Sync Panel */}
      {showNeo4jGuide && (
        <div className="container" style={{ padding:'0 1.5rem 1rem' }}>
          <div style={{ background:'#1a1200', border:'1px solid #d97706', borderRadius:'10px', padding:'1.25rem' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1rem', flexWrap:'wrap', gap:'0.5rem' }}>
              <h3 style={{ color:'#fbbf24', fontSize:'1rem' }}>
                🔗 Neo4j Desktop Integration
              </h3>
              <button
                className="btn-primary"
                onClick={handleSyncToNeo4j}
                disabled={syncing}
                style={{ fontSize:'0.82rem', padding:'0.4rem 0.85rem' }}
              >
                {syncing ? 'Syncing to Neo4j...' : '▶ Click Here to Sync All Movies to Neo4j'}
              </button>
            </div>

            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:'1rem', fontSize:'0.85rem', color:'#e2e8f0' }}>
              <div>
                <p style={{ fontWeight:700, color:'#fde68a', marginBottom:'0.4rem' }}>1. Check Neo4j Desktop</p>
                <p>In Neo4j Desktop, ensure your DBMS (named <em>MovieRecommendation</em>) is showing <strong>● Running</strong>.</p>
                <p style={{ marginTop:'0.35rem', color:'#94a3b8', fontSize:'0.8rem' }}>Default Bolt URI: <code>bolt://localhost:7687</code></p>
              </div>

              <div>
                <p style={{ fontWeight:700, color:'#fde68a', marginBottom:'0.4rem' }}>2. Password Setup</p>
                <p>The system expects password: <code style={{ background:'#0b1120', padding:'0.15rem 0.4rem', borderRadius:'4px', color:'#93c5fd' }}>password123</code></p>
                <p style={{ marginTop:'0.35rem', color:'#94a3b8', fontSize:'0.8rem' }}>If you set a different password, update <code>backend/.env</code> → <code>NEO4J_PASSWORD</code>.</p>
              </div>

              <div>
                <p style={{ fontWeight:700, color:'#fde68a', marginBottom:'0.4rem' }}>3. Sync Data with 1-Click</p>
                <p>Click the blue <strong>"Connect &amp; Sync to Neo4j"</strong> button above. All movies, genres, actors, and directors will be populated into Neo4j automatically!</p>
              </div>

              <div>
                <p style={{ fontWeight:700, color:'#fde68a', marginBottom:'0.4rem' }}>4. View in Neo4j Browser</p>
                <p>Open <strong>http://localhost:7474</strong> in your browser to visualize your graph. Run:</p>
                <code style={{ display:'block', background:'#0b1120', padding:'0.35rem 0.5rem', borderRadius:'4px', color:'#4ade80', fontSize:'0.75rem', marginTop:'0.3rem' }}>
                  MATCH (m:Movie)-[r]-&gt;(n) RETURN m,r,n LIMIT 50
                </code>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Architecture Details */}
      {expanded && (
        <div className="container" style={{ padding:'0 1.5rem 1rem' }}>
          <div style={{ background:'#131e33', borderRadius:'8px', border:'1px solid #1e3a5f', padding:'1rem', display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(200px, 1fr))', gap:'1rem', fontSize:'0.82rem', color:'#94a3b8' }}>
            <div>
              <strong style={{ color:'#f8fafc' }}>MongoDB (Document Store)</strong>
              <p>Movies: {status.data_summary?.movies}</p>
              <p>Users: {status.data_summary?.users}</p>
              <p>Ratings: {status.data_summary?.ratings}</p>
              <p>Reviews: {status.data_summary?.reviews}</p>
            </div>
            <div>
              <strong style={{ color:'#f8fafc' }}>Neo4j (Live Graph Database)</strong>
              <p>Live Nodes: {status.neo4j?.live_nodes || 0}</p>
              <p>Live Relationships: {status.neo4j?.live_relationships || 0}</p>
              <p>Labels: Movie, Genre, Actor, Director, User</p>
              <p>Relationships: IN_GENRE, ACTED_IN, DIRECTED, RATED, WATCHLISTED</p>
            </div>
            <div>
              <strong style={{ color:'#f8fafc' }}>Recommender Engine</strong>
              <p>Content Graph: Shared Director &amp; Cast matching</p>
              <p>Collaborative Filtering: Multi-hop graph paths</p>
              <p>Explainable AI: Human-readable recommendations</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
