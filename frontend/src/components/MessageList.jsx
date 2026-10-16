import React from 'react';
import { FiUser, FiZap } from 'react-icons/fi';
import MarkdownContent from './MarkdownContent';
import '../styles/MessageList.css';

function MessageList({ messages }) {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <div key={message.id} className={`message-wrapper message-${message.type}`}>
          <div className="message-avatar">
            {message.type === 'user' ? (
              <FiUser className="avatar-icon" />
            ) : (
              <FiZap className="avatar-icon" />
            )}
          </div>
          
          <div className={`message-bubble ${message.type}`}>
            {message.type === 'user' ? (
              <div className="message-text-user">{message.text}</div>
            ) : (
              <div className="message-content">
                {message.isError ? (
                  <div className="message-error">{message.text}</div>
                ) : (
                  <MarkdownContent content={message.text} />
                )}
              </div>
            )}
            
            <span className="message-time">
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default MessageList;
