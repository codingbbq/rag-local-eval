import React, { useState, useEffect } from 'react';
import { FiTrash2, FiDownload, FiChevronDown, FiChevronUp, FiSearch, FiRefreshCw } from 'react-icons/fi';
import api from '../services/api';
import '../styles/SessionList.css';

function SessionList({ onSelectSession, onCreateNew }) {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedSessions, setExpandedSessions] = useState(new Set());

    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        try {
            setLoading(true);
            setError(null);

            console.log('Loading sessions...');
            const response = await api.listSessions();

            let sessionsList = response.sessions || (Array.isArray(response) ? response : []);

            const deduplicatedSessions = [];
            const seenIds = new Set();

            for (const session of sessionsList) {
                if (session.messages && session.messages.length > 0) {
                    if (!seenIds.has(session.session_id)) {
                        deduplicatedSessions.push(session);
                        seenIds.add(session.session_id);
                    }
                }
            }

            deduplicatedSessions.sort((a, b) => {
                const dateA = new Date(a.created_at || 0);
                const dateB = new Date(b.created_at || 0);
                return dateB - dateA;
            });

            setSessions(deduplicatedSessions);
            console.log(`✅ Loaded ${deduplicatedSessions.length} sessions`);
        } catch (err) {
            console.error('Error loading sessions:', err);
            setError(err.message || 'Failed to load sessions');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteSession = async (sessionId, event) => {
        event.stopPropagation();

        if (!window.confirm('Delete this session?')) return;

        try {
            console.log('Deleting session:', sessionId);
            await api.deleteSession(sessionId);

            setSessions(prev => prev.filter(s => s.session_id !== sessionId));

            setExpandedSessions(prev => {
                const newSet = new Set(prev);
                newSet.delete(sessionId);
                return newSet;
            });

            console.log('✅ Session deleted');
        } catch (err) {
            console.error('Error deleting session:', err);
            setError(err.message || 'Failed to delete session');
        }
    };

    const handleDownloadSession = async (sessionId, event) => {
        event.stopPropagation();

        try {
            console.log('Downloading session:', sessionId);
            const text = await api.downloadSessionAsText(sessionId);

            const blob = new Blob([text], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${sessionId}.txt`;
            a.click();
            window.URL.revokeObjectURL(url);

            console.log('✅ Session downloaded');
        } catch (err) {
            console.error('Error downloading session:', err);
            setError(err.message || 'Failed to download session');
        }
    };

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

    const filteredSessions = sessions.filter(session => {
        const query = searchQuery.toLowerCase();
        return (
            session.title.toLowerCase().includes(query) ||
            (session.session_id && session.session_id.toLowerCase().includes(query))
        );
    });

    if (loading) {
        return (
            <div className="session-list-container">
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <p>Loading sessions...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="session-list-container">
            <div className="session-list-header">
                <h2 className="session-list-title">Chat Sessions</h2>
                <button className="session-refresh-btn" onClick={loadSessions} title="Refresh">
                    <FiRefreshCw /> Refresh
                </button>
            </div>

            {error && (
                <div className="session-error">
                    <span>⚠️ {error}</span>
                </div>
            )}

            <div style={{
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#1e40af',
                padding: '12px 16px',
                borderRadius: '8px',
                marginBottom: '16px',
                fontSize: '13px'
            }}>
                ℹ️ Sessions stored in SQLite backend
            </div>

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
                            <div className="session-item-content">
                                <h3 className="session-item-title">{session.title}</h3>
                                <div className="session-item-meta">
                                    <span className="session-messages">{session.messages?.length || 0}</span>
                                    <span className="session-date">
                                        {new Date(session.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            <div className="session-item-actions">
                                <button
                                    className="session-action-btn"
                                    onClick={(e) => handleDownloadSession(session.session_id, e)}
                                    title="Download"
                                >
                                    <FiDownload />
                                </button>

                                <button
                                    className="session-action-btn delete-btn"
                                    onClick={(e) => handleDeleteSession(session.session_id, e)}
                                    title="Delete"
                                >
                                    <FiTrash2 />
                                </button>

                                <button
                                    className="session-action-btn"
                                    onClick={(e) => toggleExpanded(session.session_id, e)}
                                    title="Details"
                                >
                                    {expandedSessions.has(session.session_id) ? (
                                        <FiChevronUp />
                                    ) : (
                                        <FiChevronDown />
                                    )}
                                </button>
                            </div>

                            {expandedSessions.has(session.session_id) && (
                                <div style={{
                                    gridColumn: '1 / -1',
                                    padding: '12px 16px',
                                    background: 'var(--background)',
                                    borderTop: '1px solid var(--border)',
                                    marginTop: '12px',
                                    fontSize: '12px',
                                    color: 'var(--text-secondary)'
                                }}>
                                    <div><strong>ID:</strong> {session.session_id}</div>
                                    <div><strong>Messages:</strong> {session.messages?.length || 0}</div>
                                    <div><strong>Created:</strong> {new Date(session.created_at).toLocaleString()}</div>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default SessionList;
