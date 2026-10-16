import React, { useRef, useEffect, useState } from 'react';
import { FiLoader } from 'react-icons/fi';
import MessageList from './MessageList';
import InputBox from './InputBox';
import Metrics from './Metrics';
import '../styles/Chat.css';

function Chat({ messages, loading, onSendMessage, metrics }) {
  const messagesEndRef = useRef(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const lastMessage = messages[messages.length - 1];

  // Debug: Log metrics changes
  useEffect(() => {
    console.log('Metrics updated:', metrics);
  }, [metrics]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const conversationTurn = Math.ceil((messages.length - 1) / 2);

  return (
    <div className="chat-container">
      {/* Chat Toolbar */}
      <div className="chat-toolbar">
        <div className="chat-stats">
          <div className="stat">
            <span className="stat-label">Turn</span>
            <span className="stat-value">{conversationTurn}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Messages</span>
            <span className="stat-value">{messages.length - 1}</span>
          </div>
          {metrics && metrics.overall !== undefined && (
            <div className="stat">
              <span className="stat-label">Quality</span>
              <span className="stat-value">{(metrics.overall * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
        
        {/* Only show button if we have metrics */}
        {metrics && (
          <button 
            className="metrics-toggle-btn"
            onClick={() => {
              console.log('Toggle metrics clicked, current state:', showMetrics);
              setShowMetrics(!showMetrics);
            }}
            title="Toggle metrics"
          >
            {showMetrics ? 'Hide' : 'Show'} Metrics
          </button>
        )}
      </div>

      {/* Metrics Panel - Only show if metrics exist and showMetrics is true */}
      {metrics && showMetrics && (
        <div className="metrics-panel">
          <Metrics metrics={metrics} />
        </div>
      )}

      {/* Chat Messages */}
      <div className="chat-messages">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* Off-topic Warning */}
      {lastMessage?.is_on_topic === false && (
        <div className="warning-banner">
          <span className="warning-icon">⚠</span>
          <div className="warning-content">
            <span className="warning-title">Off-topic question detected</span>
            <span className="warning-text">
              I'm designed to help with product documentation. Try asking about features, setup, or best practices.
            </span>
          </div>
        </div>
      )}

      {/* Minimal Loading Indicator */}
      {loading && (
        <div className="loading-bar">
          <FiLoader className="loading-spinner" />
          <span>Processing...</span>
        </div>
      )}

      {/* Input Box */}
      <InputBox 
        onSendMessage={onSendMessage} 
        disabled={loading}
        placeholder="Ask me anything about your documentation..."
      />
    </div>
  );
}

export default Chat;
