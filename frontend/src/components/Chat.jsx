import React, { useRef, useEffect, useState } from 'react';
import { FiLoader, FiPlus } from 'react-icons/fi';
import MessageList from './MessageList';
import InputBox from './InputBox';
import Metrics from './Metrics';
import useChatPersistence from '../hooks/useChatPersistence';
import api from '../services/api';
import '../styles/Chat.css';

function Chat({ onSessionChange, onNavigateToSessions }) {
  const messagesEndRef = useRef(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessionTitle, setSessionTitle] = useState('');

  // Use persistence hook
  const {
    sessionId,
    messages,
    isLoading: persistenceLoading,
    error: persistenceError,
    addUserMessage,
    addAssistantMessage,
    createNewSession,
    getTotalTokens
  } = useChatPersistence();

  // Notify parent when session changes
  useEffect(() => {
    if (sessionId && onSessionChange) {
      onSessionChange(sessionId);
    }
  }, [sessionId, onSessionChange]);

  // Update session title when component mounts or sessionId changes
  useEffect(() => {
    if (sessionId) {
      const title = `Chat Session - ${new Date().toLocaleString()}`;
      setSessionTitle(title);
    }
  }, [sessionId]);

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
  const totalTokens = getTotalTokens();

  const handleSendMessage = async (userMessage) => {
    if (!userMessage.trim() || !sessionId) {
      return;
    }

    try {
      setLoading(true);
      setMetrics(null);

      // Save user message to storage
      await addUserMessage(userMessage);

      // Get conversation history for context
      const conversationHistory = api.getConversationHistory();

      // Send to RAG API
      const response = await api.query(userMessage, conversationHistory);

      // Save assistant response
      await addAssistantMessage(response.answer, {
        tokensUsed: response.evaluation?.total_tokens || 0,
        isOnTopic: response.is_on_topic || true,
        sourceDocumentCount: response.num_docs_retrieved || 0,
        requestId: response.request_id || ''
      });

      // Update metrics
      setMetrics({
        faithfulness: response.evaluation?.faithfulness || 0,
        answer_relevancy: response.evaluation?.answer_relevancy || 0,
        context_precision: response.evaluation?.context_precision || 0,
        overall: response.evaluation?.overall || 0,
        num_docs: response.num_docs_retrieved || 0,
        is_on_topic: response.is_on_topic || true
      });
    } catch (error) {
      console.error('Error sending message:', error);
      // Optionally show error message to user
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNewChat = async () => {
    try {
      const timestamp = new Date().toLocaleString();
      await createNewSession(`Chat - ${timestamp}`);
      setMetrics(null);
      setShowMetrics(false);
    } catch (error) {
      console.error('Error creating new chat:', error);
    }
  };

  const lastMessage = messages[messages.length - 1];

  return (
    <div className="chat-container">
      {/* Loading state during persistence initialization */}
      {persistenceLoading && (
        <div className="loading-overlay">
          <FiLoader className="loading-spinner" />
          <span>Loading session...</span>
        </div>
      )}

      {/* Error message */}
      {persistenceError && (
        <div className="error-banner">
          <span>⚠ {persistenceError}</span>
        </div>
      )}

      {/* Chat Toolbar */}
      <div className="chat-toolbar">
        <div className="chat-stats">
          <div className="stat">
            <span className="stat-label">Turn</span>
            <span className="stat-value">{conversationTurn}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Messages</span>
            <span className="stat-value">{messages.length}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Tokens</span>
            <span className="stat-value">{totalTokens}</span>
          </div>
          {metrics && metrics.overall !== undefined && (
            <div className="stat">
              <span className="stat-label">Quality</span>
              <span className="stat-value">{(metrics.overall * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>

        <div className="chat-toolbar-actions">
          {/* New Chat Button */}
          <button
            className="new-chat-btn"
            onClick={handleCreateNewChat}
            title="Create new chat"
          >
            <FiPlus />
            <span>New Chat</span>
          </button>

          {/* Show Sessions Button */}
          <button
            className="sessions-btn"
            onClick={onNavigateToSessions}
            title="View all sessions"
          >
            📋 Sessions
          </button>

          {/* Show Metrics Button */}
          {metrics && (
            <button
              className="metrics-toggle-btn"
              onClick={() => setShowMetrics(!showMetrics)}
              title="Toggle metrics"
            >
              {showMetrics ? 'Hide' : 'Show'} Metrics
            </button>
          )}
        </div>
      </div>

      {/* Metrics Panel - Only show if metrics exist and showMetrics is true */}
      {metrics && showMetrics && (
        <div className="metrics-panel">
          <Metrics metrics={metrics} />
        </div>
      )}

      {/* Chat Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <div className="empty-icon">💬</div>
            <h2>Start a Conversation</h2>
            <p>Ask me anything about your documents</p>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Off-topic Warning */}
      {lastMessage?.type === 'assistant' && lastMessage?.isOnTopic === false && (
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
        onSendMessage={handleSendMessage}
        disabled={loading || persistenceLoading}
        placeholder="Ask me anything about your documentation..."
      />
    </div>
  );
}

export default Chat;
