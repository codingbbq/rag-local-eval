import React, { useState, useEffect } from 'react';
import { FiTrash2, FiDownload, FiRefreshCw, FiSearch } from 'react-icons/fi';
import api from '../services/api';
import '../styles/SessionList.css';

function SessionList({ onSelectSession, onCreateNew }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);
  const [selectedSessionId, setSelectedSessionId] = useState(null);

  // Load sessions on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await api.chat.listSessions(50, 0);
      setSessions(data.sessions || []);
    } catch (err) {
      setError('Failed to load sessions');
      console.error('Error loading sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);

    if (!query.trim()) {
      loadSessions();
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = await api.chat.searchSessions(query);
      setSessions(data.sessions || []);
    } catch (err) {
      setError('Failed to search sessions');
      console.error('Error searching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSession = (session) => {
    setSelectedSessionId(session.session_id);
    if (onSelectSession) {
      onSelectSession(session.session_id);
    }
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();

    if (!window.confirm('Delete this session? This cannot be undone.')) {
      return;
    }

    try {
      setError(null);
      await api.chat.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      if (selectedSessionId === sessionId) {
        setSelectedSessionId(null);
      }
    } catch (err) {
      setError('Failed to delete session');
      console.error('Error deleting session:', err);
    }
  };

  const handleDownloadSession = async (sessionId, title, e) => {
    e.stopPropagation();

    try {
      setError(null);
      const data = await api.chat.downloadSessionTxt(sessionId);

      // Create blob and download
      const blob = new Blob([data.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download session');
      console.error('Error downloading session:', err);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined,
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="session-list-container">
      <div className="session-list-header">
        <h1 className="session-list-title">Chat Sessions</h1>
        <button className="session-new-btn" onClick={onCreateNew}>
          + New Chat
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="session-error">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Search Bar */}
      <div className="session-search">
        <FiSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search sessions by title or content..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          className="search-input"
        />
        {searchQuery && (
          <button
            className="search-clear"
            onClick={() => handleSearch('')}
          >
            ✕
          </button>
        )}
      </div>

      {/* Sessions List */}
      <div className="session-list">
        {loading ? (
          <div className="session-loading">
            <div className="loading-spinner"></div>
            <p>Loading sessions...</p>
          </div>
        ) : sessions.length === 0 ? (
          <div className="session-empty">
            <p>No sessions found</p>
            <p className="session-empty-hint">
              {searchQuery
                ? 'Try a different search term'
                : 'Start a new chat to create a session'}
            </p>
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${
                selectedSessionId === session.session_id ? 'active' : ''
              }`}
              onClick={() => handleSelectSession(session)}
            >
              <div className="session-item-content">
                <div className="session-item-title">{session.title}</div>
                <div className="session-item-meta">
                  <span className="session-messages">
                    {session.message_count} message{session.message_count !== 1 ? 's' : ''}
                  </span>
                  <span className="session-tokens">
                    {session.total_tokens} tokens
                  </span>
                  <span className="session-date">
                    {formatDate(session.created_at)}
                  </span>
                </div>
                {session.tags && session.tags.length > 0 && (
                  <div className="session-tags">
                    {session.tags.map((tag, idx) => (
                      <span key={idx} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="session-item-actions">
                <button
                  className="session-action-btn download-btn"
                  onClick={(e) =>
                    handleDownloadSession(session.session_id, session.title, e)
                  }
                  title="Download as text"
                >
                  <FiDownload />
                </button>
                <button
                  className="session-action-btn delete-btn"
                  onClick={(e) => handleDeleteSession(session.session_id, e)}
                  title="Delete session"
                >
                  <FiTrash2 />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Refresh Button */}
      {!loading && (
        <button className="session-refresh-btn" onClick={loadSessions}>
          <FiRefreshCw /> Refresh
        </button>
      )}
    </div>
  );
}

export default SessionList;

