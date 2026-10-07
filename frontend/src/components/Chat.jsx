import React, { useRef, useEffect, useState } from 'react';
import MessageList from './MessageList';
import InputBox from './InputBox';
import Metrics from './Metrics';
import '../styles/Chat.css';

function Chat({ messages, loading, onSendMessage, metrics }) {
  const messagesEndRef = useRef(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (messages.length > 0) {
      setLastMessage(messages[messages.length - 1]);
    }
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-content">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {lastMessage?.is_on_topic === false && (
        <div className="off-topic-warning">
          <i className="ti ti-alert-circle"></i>
          <span>This question appears to be off-topic for Unica Campaign assistance.</span>
        </div>
      )}

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