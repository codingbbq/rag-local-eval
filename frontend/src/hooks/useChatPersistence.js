import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';

/**
 * Custom hook for chat persistence
 * Manages session creation, message storage, and retrieval
 * 
 * COMPATIBLE VERSION - Works with existing api.js methods
 */
export default function useChatPersistence() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const sessionCreatedRef = useRef(false);
  const messageCountRef = useRef(0);

  // ============================================
  // Initialize on Mount
  // ============================================

  useEffect(() => {
    const initializeSession = async () => {
      try {
        setIsLoading(true);
        
        // Create new session on mount
        const timestamp = new Date().toLocaleString();
        const newSessionId = `session_${Date.now()}`;
        
        setSessionId(newSessionId);
        setMessages([]);
        messageCountRef.current = 0;
        sessionCreatedRef.current = false;
        
        // Store in localStorage for this session
        localStorage.setItem('lastSessionId', newSessionId);
        
        console.log(`✅ New session created locally: ${newSessionId}`);
        setError(null);
      } catch (err) {
        console.error('Error initializing session:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    initializeSession();
  }, []);

  // ============================================
  // Create New Session
  // ============================================

  const createNewSession = useCallback(async (title) => {
    try {
      setIsLoading(true);
      
      // Only save previous session if it has messages
      if (sessionId && messageCountRef.current > 0 && !sessionCreatedRef.current) {
        try {
          const timestamp = new Date().toLocaleString();
          const sessionTitle = title || `Chat - ${timestamp}`;
          
          // Create the session in database with existing messages
          await api.createSession({
            title: sessionTitle,
            messages: messages
          });
          
          sessionCreatedRef.current = true;
          console.log(`✅ Previous session saved to database: ${sessionTitle}`);
        } catch (err) {
          console.warn('Could not save previous session:', err);
        }
      }
      
      // Create new local session
      const newSessionId = `session_${Date.now()}`;
      const timestamp = new Date().toLocaleString();
      
      setSessionId(newSessionId);
      setMessages([]);
      messageCountRef.current = 0;
      sessionCreatedRef.current = false;
      
      // Update localStorage
      localStorage.setItem('lastSessionId', newSessionId);
      
      setError(null);
      console.log(`📝 New session created locally: ${newSessionId}`);
    } catch (err) {
      console.error('Error creating new session:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, messages]);

  // ============================================
  // Load Existing Session
  // ============================================

  const loadSession = useCallback(async (id) => {
    try {
      setIsLoading(true);
      
      // Only save current session if it has messages
      if (sessionId && messageCountRef.current > 0 && !sessionCreatedRef.current) {
        try {
          const timestamp = new Date().toLocaleString();
          await api.createSession({
            title: `Chat - ${timestamp}`,
            messages: messages
          });
          sessionCreatedRef.current = true;
          console.log(`✅ Current session auto-saved before switching`);
        } catch (err) {
          console.warn('Could not save current session:', err);
        }
      }
      
      // Load the requested session
      const allSessions = await api.listSessions();
      const session = allSessions.sessions?.find(s => s.session_id === id);
      
      if (session) {
        setSessionId(id);
        setMessages(session.messages || []);
        messageCountRef.current = session.messages?.length || 0;
        sessionCreatedRef.current = true;
        
        // Update localStorage
        localStorage.setItem('lastSessionId', id);
        
        console.log(`📂 Session loaded: ${id} (${messageCountRef.current} messages)`);
      } else {
        console.error(`Session not found: ${id}`);
        setError(`Session ${id} not found`);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error loading session:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, messages]);

  // ============================================
  // Delete Session
  // ============================================

  const deleteSession = useCallback(async (id) => {
    try {
      await api.deleteSession(id);
      
      // If deleted session was active, create new one
      if (id === sessionId) {
        await createNewSession();
      }
      
      console.log(`🗑️  Session deleted: ${id}`);
    } catch (err) {
      console.error('Error deleting session:', err);
      setError(err.message);
    }
  }, [sessionId, createNewSession]);

  // ============================================
  // Add User Message
  // ============================================

  const addUserMessage = useCallback(async (text) => {
    try {
      const userMessage = {
        id: `msg_${Date.now()}_user`,
        type: 'user',
        content: text,
        timestamp: new Date().toISOString()
      };
      
      // Update local state
      setMessages(prev => [...prev, userMessage]);
      messageCountRef.current += 1;
      
      // Save to database only if session is already created
      if (sessionCreatedRef.current && sessionId) {
        try {
          await api.addMessageToSession(sessionId, userMessage);
        } catch (err) {
          console.warn('Could not save user message to database:', err);
        }
      }
      
      console.log(`📤 User message added (${messageCountRef.current} total)`);
    } catch (err) {
      console.error('Error adding user message:', err);
      setError(err.message);
    }
  }, [sessionId]);

  // ============================================
  // Add Assistant Message (Auto-save first exchange)
  // ============================================

  const addAssistantMessage = useCallback(async (text, metadata = {}) => {
    try {
      // Auto-create session on first assistant message (when user has sent a message)
      if (!sessionCreatedRef.current && sessionId && messageCountRef.current > 0) {
        try {
          const timestamp = new Date().toLocaleString();
          await api.createSession({
            title: `Chat - ${timestamp}`,
            messages: messages
          });
          sessionCreatedRef.current = true;
          console.log(`✅ Session auto-saved on first exchange`);
        } catch (err) {
          console.warn('Could not auto-save session:', err);
        }
      }
      
      const assistantMessage = {
        id: `msg_${Date.now()}_assistant`,
        type: 'assistant',
        content: text,
        timestamp: new Date().toISOString(),
        ...metadata
      };
      
      // Update local state
      setMessages(prev => [...prev, assistantMessage]);
      messageCountRef.current += 1;
      
      // Save to database if session is created
      if (sessionCreatedRef.current && sessionId) {
        try {
          await api.addMessageToSession(sessionId, assistantMessage);
        } catch (err) {
          console.warn('Could not save assistant message to database:', err);
        }
      }
      
      console.log(`📥 Assistant message added (${messageCountRef.current} total)`);
    } catch (err) {
      console.error('Error adding assistant message:', err);
      setError(err.message);
    }
  }, [sessionId, messages]);

  // ============================================
  // Clear Messages (Keep Session)
  // ============================================

  const clearMessages = useCallback(() => {
    setMessages([]);
    messageCountRef.current = 0;
    console.log('🧹 Messages cleared');
  }, []);

  // ============================================
  // Get Conversation History
  // ============================================

  const getConversationHistory = useCallback(() => {
    return messages.map(msg => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.content
    }));
  }, [messages]);

  // ============================================
  // Export Session
  // ============================================

  const exportSession = useCallback(async (id) => {
    try {
      const data = await api.exportSession(id);
      return data;
    } catch (err) {
      console.error('Error exporting session:', err);
      setError(err.message);
      return null;
    }
  }, []);

  // ============================================
  // Download Session as Text
  // ============================================

  const downloadSessionAsText = useCallback(async (id) => {
    try {
      const text = await api.downloadSessionAsText(id);
      
      // Create blob and download
      const blob = new Blob([text], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session_${id}.txt`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      console.log('📥 Session downloaded');
    } catch (err) {
      console.error('Error downloading session:', err);
      setError(err.message);
    }
  }, []);

  // ============================================
  // Get Total Tokens
  // ============================================

  const getTotalTokens = useCallback(() => {
    return messages.reduce((total, msg) => {
      return total + (msg.tokensUsed || 0);
    }, 0);
  }, [messages]);

  // ============================================
  // Get Session Stats
  // ============================================

  const getSessionStats = useCallback(() => {
    return {
      sessionId,
      messageCount: messages.length,
      userMessages: messages.filter(m => m.type === 'user').length,
      assistantMessages: messages.filter(m => m.type === 'assistant').length,
      totalTokens: getTotalTokens(),
      isSaved: sessionCreatedRef.current
    };
  }, [sessionId, messages, getTotalTokens]);

  // ============================================
  // Return Public API
  // ============================================

  return {
    sessionId,
    messages,
    isLoading,
    error,
    
    // Session management
    createNewSession,
    loadSession,
    deleteSession,
    
    // Message management
    addUserMessage,
    addAssistantMessage,
    clearMessages,
    
    // Data retrieval
    getConversationHistory,
    getTotalTokens,
    getSessionStats,
    
    // Export
    exportSession,
    downloadSessionAsText,
    
    // Status
    isSaved: sessionCreatedRef.current,
    messageCount: messages.length
  };
}