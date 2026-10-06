import React, { useRef, useEffect, useState } from 'react';
import MessageList from './MessageList';
import InputBox from './InputBox';
import Metrics from './Metrics';
import '../styles/Chat.css';

function Chat({ messages, loading, onSendMessage, metrics }) {
  const messagesEndRef = useRef(null);
  const [showMetrics, setShowMetrics] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-content">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {metrics && (
        <div className="metrics-toggle">
          <button 
            className="toggle-button"
            onClick={() => setShowMetrics(!showMetrics)}
          >
            {showMetrics ? 'Hide' : 'Show'} Metrics
          </button>
          {showMetrics && <Metrics metrics={metrics} />}
        </div>
      )}

      <InputBox 
        onSendMessage={onSendMessage} 
        disabled={loading}
      />
    </div>
  );
}

export default Chat;
