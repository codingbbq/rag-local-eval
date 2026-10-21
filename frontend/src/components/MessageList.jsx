import React from 'react';
import { FiUser, FiZap } from 'react-icons/fi';
import MarkdownContent from './MarkdownContent';
import '../styles/MessageList.css';

/**
 * MessageList Component
 * Displays all messages in the conversation
 */
function MessageList({ messages = [] }) {
  // ============================================
  // Format Timestamp
  // ============================================

  const formatTime = (timestamp) => {
    try {
      // If it's already a string, convert it to a Date
      if (typeof timestamp === 'string') {
        const date = new Date(timestamp);
        // Check if date is valid
        if (isNaN(date.getTime())) {
          return 'just now';
        }
        return date.toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        });
      }
      
      // If it's already a Date object
      if (timestamp instanceof Date) {
        if (isNaN(timestamp.getTime())) {
          return 'just now';
        }
        return timestamp.toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        });
      }
      
      // Fallback
      return 'just now';
    } catch (error) {
      console.warn('Error formatting timestamp:', error);
      return 'just now';
    }
  };

  // ============================================
  // Render
  // ============================================

  return (
    <div className="message-list">
      {messages && messages.length > 0 ? (
        messages.map((message, index) => (
          <div
            key={message.id || index}
            className={`message message-${message.type}`}
          >
            {/* Avatar */}
            <div className="message-avatar">
              {message.type === 'user' ? (
                <FiUser className="avatar-icon user-icon" />
              ) : (
                <FiZap className="avatar-icon assistant-icon" />
              )}
            </div>

            {/* Content */}
            <div className="message-content-wrapper">
              {/* Header */}
              <div className="message-header">
                <span className="message-role">
                  {message.type === 'user' ? 'You' : 'Assistant'}
                </span>
                <span className="message-time">
                  {formatTime(message.timestamp)}
                </span>
              </div>

              {/* Message Content */}
              <div className="message-content">
                {message.type === 'user' ? (
                  <p className="message-text">{message.content}</p>
                ) : (
                  <MarkdownContent content={message.content} />
                )}
              </div>

              {/* Metadata */}
              {message.type === 'assistant' && message.isOnTopic !== undefined && (
                <div className="message-metadata">
                  <span 
                    className={`on-topic-badge ${message.isOnTopic ? 'relevant' : 'off-topic'}`}
                  >
                    {message.isOnTopic ? '✓ On topic' : '⚠ Off topic'}
                  </span>
                  {message.sourceDocumentCount !== undefined && (
                    <span className="doc-count-badge">
                      📄 {message.sourceDocumentCount} {message.sourceDocumentCount === 1 ? 'doc' : 'docs'}
                    </span>
                  )}
                  {message.tokensUsed !== undefined && (
                    <span className="tokens-badge">
                      🔢 {message.tokensUsed} tokens
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))
      ) : (
        <div className="message-list-empty">
          <div className="empty-icon">💭</div>
          <p>No messages yet</p>
          <p className="empty-hint">Start a conversation to see messages here</p>
        </div>
      )}
    </div>
  );
}

export default MessageList;
