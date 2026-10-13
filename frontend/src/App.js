import React, { useState, useEffect } from 'react';
import './styles/App.css';
import Chat from './components/Chat';
import UploadPage from './pages/UploadPage';

function App() {
    const [currentPage, setCurrentPage] = useState('chat'); // 'chat' or 'upload'
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

    // Load conversation history on page load
    useEffect(() => {
        const loadConversationHistory = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/v1/conversation/history');
                if (response.ok) {
                    const data = await response.json();

                    if (data.history && data.history.length > 0) {
                        // Convert backend history to frontend messages
                        const loadedMessages = data.history.map((msg, idx) => ({
                            id: idx + 2,
                            type: msg.role === 'user' ? 'user' : 'assistant',
                            text: msg.content,
                            timestamp: new Date(msg.timestamp)
                        }));

                        // Prepend welcome message and loaded history
                        setMessages([messages[0], ...loadedMessages]);
                        console.log(`📚 Loaded ${loadedMessages.length} messages from backend`);
                    }
                }
            } catch (error) {
                console.error('Error loading conversation history:', error);
            }
        };

        // Only load on initial page load
        if (messages.length === 1) {
            loadConversationHistory();
        }
    }, []); // Empty dependency array = run once on mount

    const handleSendMessage = async (userMessage) => {
        const newUserMessage = {
            id: messages.length + 1,
            type: 'user',
            text: userMessage,
            timestamp: new Date()
        };

        setMessages([...messages, newUserMessage]);
        setLoading(true);

        try {
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

            const newAssistantMessage = {
                id: messages.length + 2,
                type: 'assistant',
                text: data.answer,
                timestamp: new Date(),
                metrics: data.evaluation,
                is_on_topic: data.is_on_topic
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
                <h1>🤖 RAG Chat System</h1>
                <p>Document Question Answering with Evaluation</p>
                <nav className="header-nav">
                    <button
                        className={`nav-btn ${currentPage === 'chat' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('chat')}
                    >
                        💬 Chat
                    </button>
                    <button
                        className={`nav-btn ${currentPage === 'upload' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('upload')}
                    >
                        📚 Upload
                    </button>
                </nav>
            </header>

            <main className="app-main">
                {currentPage === 'chat' && (
                    <Chat
                        messages={messages}
                        loading={loading}
                        onSendMessage={handleSendMessage}
                        metrics={metrics}
                    />
                )}
                {currentPage === 'upload' && <UploadPage />}
            </main>
        </div>
    );
}

export default App;