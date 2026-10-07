import React from 'react';
import MarkdownContent from './MarkdownContent';
import '../styles/MessageList.css';

function MessageList({ messages }) {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <div 
          key={message.id} 
          className={`message message-${message.type}`}
        >
          <div className="message-content">
            {message.type === 'assistant' ? (
              <MarkdownContent content={message.text} />
            ) : (
              <p>{message.text}</p>
            )}
          </div>
          <span className="message-time">
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
        </div>
      ))}
    </div>
  );
}

export default MessageList;