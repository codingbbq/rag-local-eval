import React, { useState, useEffect } from 'react';
import { FiMenu, FiX, FiMessageSquare, FiUploadCloud, FiSettings } from 'react-icons/fi';
import { BiLogoDribbble } from 'react-icons/bi';
import './styles/App.css';
import Chat from './components/Chat';
import UploadPage from './pages/UploadPage';

function App() {
  const [currentPage, setCurrentPage] = useState('chat');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: 'Welcome to DocAssistant. Ask me anything about your product documentation, and I\'ll provide detailed, accurate answers.',
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  // Load conversation history on mount
  useEffect(() => {
    const loadConversationHistory = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/conversation/history');
        if (response.ok) {
          const data = await response.json();
          
          if (data.history && data.history.length > 0) {
            const loadedMessages = data.history.map((msg, idx) => ({
              id: idx + 2,
              type: msg.role === 'user' ? 'user' : 'assistant',
              text: msg.content,
              timestamp: new Date(msg.timestamp)
            }));
            
            setMessages([messages[0], ...loadedMessages]);
          }
        }
      } catch (error) {
        console.error('Error loading conversation history:', error);
      }
    };

    if (messages.length === 1) {
      loadConversationHistory();
    }
  }, [messages]);

  const handleSendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;

    const userMessageObj = {
      id: messages.length + 1,
      type: 'user',
      text: userMessage,
      timestamp: new Date()
    };
    setMessages([...messages, userMessageObj]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage })
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();

      const assistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: data.answer,
        timestamp: new Date(),
        is_on_topic: data.is_on_topic,
        conversation_turn: data.conversation_turn
      };

      setMessages(prev => [...prev, assistantMessage]);
      setMetrics({
        faithfulness: data.evaluation?.faithfulness || 0,
        answer_relevancy: data.evaluation?.answer_relevancy || 0,
        context_precision: data.evaluation?.context_precision || 0,
        overall: data.evaluation?.overall || 0,
        num_docs: data.num_docs_retrieved,
        is_on_topic: data.is_on_topic
      });

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (window.confirm('Are you sure you want to clear this conversation?')) {
      try {
        await fetch('http://localhost:8000/api/v1/conversation/clear', {
          method: 'DELETE'
        });
        setMessages([
          {
            id: 1,
            type: 'assistant',
            text: 'Welcome to DocAssistant. Ask me anything about your product documentation.',
            timestamp: new Date()
          }
        ]);
        setMetrics(null);
      } catch (error) {
        console.error('Error clearing chat:', error);
      }
    }
  };

  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: FiMessageSquare },
    { id: 'upload', label: 'Upload Documents', icon: FiUploadCloud },
    { id: 'settings', label: 'Settings', icon: FiSettings },
  ];

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <nav className="navbar">
        <div className="navbar-container">
          {/* Logo */}
          <div className="navbar-logo">
            <BiLogoDribbble className="logo-icon" />
            <span className="logo-text">DocAssistant</span>
          </div>

          {/* Desktop Navigation */}
          <div className="nav-links-desktop">
            {navigationItems.map(item => {
              const IconComponent = item.icon;
              return (
                <button
                  key={item.id}
                  className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
                  onClick={() => {
                    setCurrentPage(item.id);
                    setMobileMenuOpen(false);
                  }}
                >
                  <IconComponent className="nav-icon" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Right side actions */}
          <div className="navbar-right">
            {currentPage === 'chat' && (
              <button 
                className="clear-btn"
                onClick={handleClearChat}
                title="Clear conversation"
              >
                Clear Chat
              </button>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <FiX size={24} />
            ) : (
              <FiMenu size={24} />
            )}
          </button>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="nav-links-mobile">
            {navigationItems.map(item => {
              const IconComponent = item.icon;
              return (
                <button
                  key={item.id}
                  className={`nav-link-mobile ${currentPage === item.id ? 'active' : ''}`}
                  onClick={() => {
                    setCurrentPage(item.id);
                    setMobileMenuOpen(false);
                  }}
                >
                  <IconComponent className="nav-icon" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {currentPage === 'chat' && (
          <Chat 
            messages={messages}
            loading={loading}
            onSendMessage={handleSendMessage}
            metrics={metrics}
          />
        )}
        {currentPage === 'upload' && (
          <UploadPage />
        )}
        {currentPage === 'settings' && (
          <div className="settings-page">
            <div className="settings-container">
              <h1>Settings</h1>
              <p>Settings page - Coming soon</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;