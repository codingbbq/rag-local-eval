import React, { useState } from 'react';
import { FiMenu, FiX, FiMessageSquare, FiUploadCloud, FiSettings, FiClock } from 'react-icons/fi';
import Chat from './components/Chat';
import UploadPage from './pages/UploadPage';
import SessionList from './components/SessionList';
import './styles/App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('chat');
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: FiMessageSquare },
    { id: 'sessions', label: 'Sessions', icon: FiClock },
    { id: 'upload', label: 'Upload Documents', icon: FiUploadCloud },
    { id: 'settings', label: 'Settings', icon: FiSettings }
  ];

  const handleNavigateToPage = (pageId) => {
    setCurrentPage(pageId);
    setMenuOpen(false);
  };

  const handleSessionSelect = (sessionId) => {
    setCurrentSessionId(sessionId);
    setCurrentPage('chat');
  };

  const handleNavigateToSessions = () => {
    setCurrentPage('sessions');
  };

  const handleCreateNewChat = () => {
    setCurrentSessionId(null);
    setCurrentPage('chat');
  };

  return (
    <div className="app">
      {/* Top Navbar */}
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-left">
            <button
              className="menu-toggle"
              onClick={() => setMenuOpen(!menuOpen)}
              title="Toggle menu"
            >
              {menuOpen ? <FiX /> : <FiMenu />}
            </button>
            <h1 className="navbar-title">RAG Chat</h1>
          </div>

          {/* Navigation Items */}
          <div className={`nav-items ${menuOpen ? 'open' : ''}`}>
            {navigationItems.map(item => (
              <button
                key={item.id}
                className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => handleNavigateToPage(item.id)}
                title={item.label}
              >
                <item.icon className="nav-icon" />
                <span className="nav-label">{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="main-content">
        {currentPage === 'chat' && (
          <Chat
            onSessionChange={setCurrentSessionId}
            onNavigateToSessions={handleNavigateToSessions}
          />
        )}

        {currentPage === 'sessions' && (
          <SessionList
            onSelectSession={handleSessionSelect}
            onCreateNew={handleCreateNewChat}
          />
        )}

        {currentPage === 'upload' && <UploadPage />}

        {currentPage === 'settings' && (
          <div className="settings-placeholder">
            <div className="placeholder-content">
              <div className="placeholder-icon">⚙️</div>
              <h2>Settings</h2>
              <p>Settings page coming soon</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;