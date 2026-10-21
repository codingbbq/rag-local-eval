import React, { useState, useEffect } from 'react';
import { FiTrash2, FiDownload, FiChevronDown, FiChevronUp, FiSearch } from 'react-icons/fi';
import '../styles/SessionList.css';

/**
 * SessionList Component - Fallback Version
 * Uses localStorage instead of API calls
 * 
 * NOTE: Sessions stored in localStorage only (not persistent across devices)
 * To use backend persistence, implement API methods in your api.js
 */
function SessionList({ onSelectSession, onCreateNew }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSessions, setExpandedSessions] = useState(new Set());

  // ============================================
  // Load Sessions on Mount
  // ============================================

  useEffect(() => {
    loadSessions();
  }, []);

  // ============================================
  // Load Sessions from localStorage
  // ============================================

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try API first
      try {
        // Attempt to call API method (if it exists)
        const response = await fetchSessionsFromAPI();
        if (response && response.sessions) {
          setSessions(response.sessions);
          console.log(`✅ Loaded ${response.sessions.length} sessions from backend`);
          setLoading(false);
          return;
        }
      } catch (apiError) {
        console.log('⚠️  Backend API not available, using localStorage');
      }

      // Fallback to localStorage
      const sessionsKey = 'rag_chat_sessions';
      const stored = localStorage.getItem(sessionsKey);
      
      let sessionsList = [];
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          sessionsList = Array.isArray(parsed) ? parsed : [];
        } catch (e) {
          console.error('Error parsing stored sessions:', e);
          sessionsList = [];
        }
      }

      // Filter out empty sessions and deduplicate
      const deduplicatedSessions = [];
      const seenIds = new Set();

      for (const session of sessionsList) {
        // Only include sessions with messages
        if (session.messages && session.messages.length > 0) {
          if (!seenIds.has(session.session_id)) {
            deduplicatedSessions.push(session);
            seenIds.add(session.session_id);
          }
        }
      }

      // Sort by created_at descending
      deduplicatedSessions.sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB - dateA;
      });

      setSessions(deduplicatedSessions);
      console.log(
        `✅ Loaded ${deduplicatedSessions.length} sessions from localStorage`
      );
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // Try to Fetch from API
  // ============================================

  const fetchSessionsFromAPI = async () => {
    // This will try to call the API if available
    // If not, it will throw and we fall back to localStorage
    const response = await fetch('/api/v1/chat/sessions/list');
    if (!response.ok) throw new Error('API not available');
    return await response.json();
  };

  // ============================================
  // Handle Delete Session
  // ============================================

  const handleDeleteSession = async (sessionId, event) => {
    event.stopPropagation();

    if (!window.confirm('Are you sure you want to delete this session?')) {
      return;
    }

    try {
      // Try to delete from API
      try {
        await fetch(`/api/v1/chat/session/${sessionId}`, { method: 'DELETE' });
        console.log('✅ Session deleted from backend');
      } catch (apiError) {
        console.log('⚠️  Could not delete from backend, using localStorage');
      }

      // Remove from local state
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));

      // Remove from localStorage
      const sessionsKey = 'rag_chat_sessions';
      const stored = localStorage.getItem(sessionsKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        const updated = parsed.filter(s => s.session_id !== sessionId);
        localStorage.setItem(sessionsKey, JSON.stringify(updated));
      }

      // Clean up expanded state
      setExpandedSessions(prev => {
        const newSet = new Set(prev);
        newSet.delete(sessionId);
        return newSet;
      });

      console.log(`🗑️  Session deleted: ${sessionId}`);
    } catch (err) {
      console.error('Error deleting session:', err);
      setError(err.message);
    }
  };

  // ============================================
  // Handle Download Session
  // ============================================

  const handleDownloadSession = async (sessionId, event) => {
    event.stopPropagation();

    try {
      // Find session
      const session = sessions.find(s => s.session_id === sessionId);
      if (!session) {
        throw new Error('Session not found');
      }

      // Format as text
      let text = `Chat Session: ${session.title}\n`;
      text += `Session ID: ${sessionId}\n`;
      text += `Created: ${new Date(session.created_at).toLocaleString()}\n`;
      text += `Messages: ${session.messages?.length || 0}\n`;
      text += '\n' + '='.repeat(60) + '\n\n';

      if (session.messages && Array.isArray(session.messages)) {
        for (const msg of session.messages) {
          const role = msg.type === 'user' ? 'You' : 'Assistant';
          text += `${role}:\n${msg.content}\n\n`;
        }
      }

      // Create blob and download
      const blob = new Blob([text], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session_${sessionId}.txt`;
      a.click();
      window.URL.revokeObjectURL(url);

      console.log(`📥 Session downloaded: ${sessionId}`);
    } catch (err) {
      console.error('Error downloading session:', err);
      setError(err.message);
    }
  };

  // ============================================
  // Toggle Expanded Session
  // ============================================

  const toggleExpanded = (sessionId, event) => {
    event.stopPropagation();

    setExpandedSessions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sessionId)) {
        newSet.delete(sessionId);
      } else {
        newSet.add(sessionId);
      }
      return newSet;
    });
  };

  // ============================================
  // Filter Sessions by Search Query
  // ============================================

  const filteredSessions = sessions.filter(session => {
    const query = searchQuery.toLowerCase();
    return (
      session.title.toLowerCase().includes(query) ||
      (session.session_id && session.session_id.toLowerCase().includes(query))
    );
  });

  // ============================================
  // Render
  // ============================================

  if (loading) {
    return (
      <div className="session-list-container">
        <div className="loading">Loading sessions...</div>
      </div>
    );
  }

  return (
    <div className="session-list-container">
      {/* Header - Only Title, No New Chat Button (Already in navbar) */}
      <div className="session-list-header">
        <h2 className="session-list-title">Chat Sessions</h2>
      </div>

      {/* Error Message */}
      {error && (
        <div className="session-error">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Info Banner */}
      <div style={{
        background: 'rgba(59, 130, 246, 0.1)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        color: '#1e40af',
        padding: '12px 16px',
        borderRadius: '8px',
        marginBottom: '16px',
        fontSize: '13px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span>ℹ️</span>
        <span>Using localStorage. For persistent sessions across devices, implement backend API.</span>
      </div>

      {/* Search Bar */}
      <div className="session-search">
        <FiSearch className="search-icon" />
        <input
          type="text"
          className="search-input"
          placeholder="Search sessions..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Sessions List */}
      <div className="session-list">
        {filteredSessions.length === 0 ? (
          <div className="session-empty">
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>💬</div>
            <p>No chat sessions yet</p>
            <p className="session-empty-hint">Create a new chat to get started</p>
          </div>
        ) : (
          filteredSessions.map(session => (
            <div
              key={session.session_id}
              className="session-item"
              onClick={() => onSelectSession(session.session_id)}
            >
              {/* Session Content */}
              <div className="session-item-content">
                <h3 className="session-item-title">{session.title}</h3>
                <div className="session-item-meta">
                  <span className="session-messages">{session.messages?.length || 0}</span>
                  <span className="session-date">
                    {new Date(session.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="session-item-actions">
                <button
                  className="session-action-btn"
                  onClick={(e) => handleDownloadSession(session.session_id, e)}
                  title="Download session as text"
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

                <button
                  className="session-action-btn"
                  onClick={(e) => toggleExpanded(session.session_id, e)}
                  title="Toggle details"
                >
                  {expandedSessions.has(session.session_id) ? (
                    <FiChevronUp />
                  ) : (
                    <FiChevronDown />
                  )}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default SessionList;
