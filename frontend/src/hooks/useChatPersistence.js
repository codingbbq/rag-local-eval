import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';

export default function useChatPersistence() {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const sessionCreatedRef = useRef(false);

    useEffect(() => {
        const initializeSession = async () => {
            try {
                setIsLoading(true);
                setError(null);

                const lastSessionId = localStorage.getItem('lastSessionId');

                if (lastSessionId) {
                    try {
                        console.log('Loading session:', lastSessionId);
                        const session = await api.getSession(lastSessionId);
                        setSessionId(lastSessionId);
                        setMessages(session.messages || []);
                        sessionCreatedRef.current = true;
                        console.log('✅ Session loaded from backend');
                    } catch (err) {
                        console.warn('Session not found, creating new');
                        await createNewSession();
                    }
                } else {
                    await createNewSession();
                }
            } catch (err) {
                console.error('Error initializing:', err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        initializeSession();
    }, []);

    const createNewSession = useCallback(async () => {
        try {
            setIsLoading(true);
            const newSessionId = `session_${Date.now()}`;

            console.log('Creating session in backend');
            const response = await api.createSession({
                title: `Chat ${new Date().toLocaleDateString()}`,
                messages: []
            });

            const createdSessionId = response.session_id || newSessionId;
            setSessionId(createdSessionId);
            setMessages([]);
            sessionCreatedRef.current = true;
            localStorage.setItem('lastSessionId', createdSessionId);

            console.log('✅ New session created:', createdSessionId);
            return createdSessionId;
        } catch (err) {
            console.error('Error creating session:', err);
            setError(err.message);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const addUserMessage = useCallback(async (content) => {
        try {
            if (!sessionId) throw new Error('No active session');

            const userMessage = {
                id: `msg_${Date.now()}_${Math.random()}`,
                type: 'user',
                content,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, userMessage]);
            await api.addMessageToSession(sessionId, userMessage);
            console.log('✅ User message saved');

            return userMessage;
        } catch (err) {
            console.error('Error adding user message:', err);
            setError(err.message);
            throw err;
        }
    }, [sessionId]);

    const addAssistantMessage = useCallback(async (content, metadata = {}) => {
        try {
            if (!sessionId) throw new Error('No active session');

            const assistantMessage = {
                id: `msg_${Date.now()}_${Math.random()}`,
                type: 'assistant',
                content,
                timestamp: new Date().toISOString(),
                isOnTopic: metadata.isOnTopic,
                sourceDocumentCount: metadata.sourceDocumentCount,
                tokensUsed: metadata.tokensUsed || 0
            };

            setMessages(prev => [...prev, assistantMessage]);
            await api.addMessageToSession(sessionId, assistantMessage);
            console.log('✅ Assistant message saved');

            return assistantMessage;
        } catch (err) {
            console.error('Error adding assistant message:', err);
            setError(err.message);
            throw err;
        }
    }, [sessionId]);

    const loadSession = useCallback(async (id) => {
        try {
            setIsLoading(true);
            setError(null);

            console.log('Loading session:', id);
            const session = await api.getSession(id);

            setSessionId(id);
            setMessages(session.messages || []);
            sessionCreatedRef.current = true;
            localStorage.setItem('lastSessionId', id);

            console.log('✅ Session loaded');
            return session;
        } catch (err) {
            console.error('Error loading session:', err);
            setError(err.message);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const deleteSession = useCallback(async (id) => {
        try {
            console.log('Deleting session:', id);
            await api.deleteSession(id);

            if (localStorage.getItem('lastSessionId') === id) {
                localStorage.removeItem('lastSessionId');
            }

            console.log('✅ Session deleted');
        } catch (err) {
            console.error('Error deleting session:', err);
            setError(err.message);
            throw err;
        }
    }, []);

    const getTotalTokens = useCallback(() => {
        return messages.reduce((total, msg) => {
            return total + (msg.tokensUsed || 0);
        }, 0);
    }, [messages]);

    const getSessionStats = useCallback(() => {
        return {
            totalMessages: messages.length,
            userMessages: messages.filter(m => m.type === 'user').length,
            assistantMessages: messages.filter(m => m.type === 'assistant').length,
            totalTokens: getTotalTokens(),
            onTopicMessages: messages.filter(m => m.isOnTopic === true).length,
            offTopicMessages: messages.filter(m => m.isOnTopic === false).length
        };
    }, [messages, getTotalTokens]);

    const clearCurrentChat = useCallback(() => {
        setMessages([]);
    }, []);

    const exportSession = useCallback(async (id) => {
        try {
            console.log('Exporting session:', id);
            const data = await api.exportSession(id);
            console.log('✅ Session exported');
            return data;
        } catch (err) {
            console.error('Error exporting session:', err);
            setError(err.message);
            throw err;
        }
    }, []);

    const downloadSessionAsText = useCallback(async (id) => {
        try {
            console.log('Downloading session as text:', id);
            const text = await api.downloadSessionAsText(id);
            console.log('✅ Session downloaded');
            return text;
        } catch (err) {
            console.error('Error downloading session:', err);
            setError(err.message);
            throw err;
        }
    }, []);

    return {
        sessionId,
        messages,
        isLoading,
        error,
        createNewSession,
        loadSession,
        deleteSession,
        clearCurrentChat,
        addUserMessage,
        addAssistantMessage,
        exportSession,
        downloadSessionAsText,
        getTotalTokens,
        getSessionStats
    };
}