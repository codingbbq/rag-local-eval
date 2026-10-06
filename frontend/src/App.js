import React, { useState, useRef, useEffect } from 'react';
import './styles/App.css';
import Chat from './components/Chat';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: 'Hello! I am your RAG assistant. Ask me questions about the documents.',
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  const handleSendMessage = async (userMessage) => {
    // Add user message
    const newUserMessage = {
      id: messages.length + 1,
      type: 'user',
      text: userMessage,
      timestamp: new Date()
    };
    
    setMessages([...messages, newUserMessage]);
    setLoading(true);

    try {
      // Call backend API
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          top_k: 5
        })
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();

      // Add assistant message
      const newAssistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: data.answer,
        timestamp: new Date(),
        metrics: data.evaluation
      };

      setMessages(prev => [...prev, newAssistantMessage]);
      setMetrics(data.evaluation);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>RAG Chat</h1>
        <p>Document Question Answering with Evaluation</p>
      </header>
      
      <main className="app-main">
        <Chat 
          messages={messages} 
          loading={loading} 
          onSendMessage={handleSendMessage}
          metrics={metrics}
        />
      </main>
    </div>
  );
}

export default App;