/**
 * useChatPersistence Hook
 * Manages chat session creation, message saving, and retrieval
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import storage from '../services/storage';

export const useChatPersistence = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // ============================================
  // INITIALIZE SESSION ON MOUNT
  // ============================================

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Check if we have a current session
      let currentSessionId = storage.getCurrentSessionId();

      if (currentSessionId) {
        // Load existing session
        try {
          const session = await api.chat.getSession(currentSessionId);
          setSessionId(session.session_id);
          
          // Convert to message format
          const formattedMessages = session.messages.map((msg, idx) => ({
            id: msg.id,
            text: msg.content,
            type: msg.role,
            timestamp: new Date(msg.timestamp),
            tokensUsed: msg.tokens_used,
            isOnTopic: msg.is_on_topic,
            sourceDocumentCount: msg.source_document_count,
            requestId: msg.request_id
          }));
          
          setMessages(formattedMessages);
          
          // Cache messages locally
          storage.setCacheMessages(formattedMessages);
        } catch (err) {
          console.warn('Could not load existing session, creating new one:', err);
          // Create new session if loading fails
          await createNewSession();
        }
      } else {
        // Create new session
        await createNewSession();
      }
    } catch (err) {
      setError(err.message);
      console.error('Error initializing session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================
  // SESSION MANAGEMENT
  // ============================================

  const createNewSession = useCallback(async (title = null) => {
    try {
      setIsLoading(true);
      setError(null);

      const sessionTitle = title || `Chat Session - ${new Date().toLocaleString()}`;
      const sessionData = await api.chat.createSession(sessionTitle);
      
      setSessionId(sessionData.session_id);
      storage.setCurrentSessionId(sessionData.session_id);
      storage.addToSessionHistory({
        session_id: sessionData.session_id,
        title: sessionData.title,
        created_at: sessionData.created_at,
        message_count: 0
      });
      
      setMessages([]);
      storage.clearCachedMessages();
      
      return sessionData.session_id;
    } catch (err) {
      setError(err.message);
      console.error('Error creating session:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadSession = useCallback(async (loadSessionId) => {
    try {
      setIsLoading(true);
      setError(null);

      const session = await api.chat.getSession(loadSessionId);
      
      setSessionId(session.session_id);
      storage.setCurrentSessionId(session.session_id);
      
      // Convert to message format
      const formattedMessages = session.messages.map((msg, idx) => ({
        id: msg.id,
        text: msg.content,
        type: msg.role,
        timestamp: new Date(msg.timestamp),
        tokensUsed: msg.tokens_used,
        isOnTopic: msg.is_on_topic,
        sourceDocumentCount: msg.source_document_count,
        requestId: msg.request_id
      }));
      
      setMessages(formattedMessages);
      storage.setCacheMessages(formattedMessages);
      
      return formattedMessages;
    } catch (err) {
      setError(err.message);
      console.error('Error loading session:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteSession = useCallback(async (deleteSessionId) => {
    try {
      setError(null);
      
      await api.chat.deleteSession(deleteSessionId);
      storage.removeFromSessionHistory(deleteSessionId);
      
      // If we deleted the current session, create a new one
      if (deleteSessionId === sessionId) {
        await createNewSession();
      }
      
      return true;
    } catch (err) {
      setError(err.message);
      console.error('Error deleting session:', err);
      throw err;
    }
  }, [sessionId, createNewSession]);

  // ============================================
  // MESSAGE MANAGEMENT
  // ============================================

  const addUserMessage = useCallback(async (content) => {
    if (!sessionId) {
      setError('No active session');
      return null;
    }

    try {
      setError(null);

      // Add message to backend
      await api.chat.addMessage(
        sessionId,
        content,
        'user',
        {
          tokensUsed: estimateTokens(content),
          isOnTopic: true
        }
      );

      // Add to local state
      const newMessage = {
        id: `msg-${Date.now()}`,
        text: content,
        type: 'user',
        timestamp: new Date(),
        tokensUsed: estimateTokens(content),
        isOnTopic: true,
        sourceDocumentCount: 0
      };

      setMessages(prev => [...prev, newMessage]);
      
      return newMessage;
    } catch (err) {
      setError(err.message);
      console.error('Error adding user message:', err);
      throw err;
    }
  }, [sessionId]);

  const addAssistantMessage = useCallback(async (content, options = {}) => {
    if (!sessionId) {
      setError('No active session');
      return null;
    }

    try {
      setError(null);

      const {
        tokensUsed = 0,
        isOnTopic = true,
        sourceDocumentCount = 0,
        requestId = ''
      } = options;

      // Add message to backend
      await api.chat.addMessage(
        sessionId,
        content,
        'assistant',
        {
          tokensUsed,
          isOnTopic,
          sourceDocumentCount,
          requestId
        }
      );

      // Add to local state
      const newMessage = {
        id: `msg-${Date.now()}`,
        text: content,
        type: 'assistant',
        timestamp: new Date(),
        tokensUsed,
        isOnTopic,
        sourceDocumentCount,
        requestId
      };

      setMessages(prev => [...prev, newMessage]);
      
      return newMessage;
    } catch (err) {
      setError(err.message);
      console.error('Error adding assistant message:', err);
      throw err;
    }
  }, [sessionId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    storage.clearCachedMessages();
  }, []);

  // ============================================
  // UTILITY FUNCTIONS
  // ============================================

  /**
   * Estimate token count (rough approximation)
   * 1 token ≈ 4 characters
   */
  const estimateTokens = (text) => {
    return Math.ceil(text.length / 4);
  };

  /**
   * Get conversation history for RAG context
   */
  const getConversationHistory = useCallback(() => {
    return messages.map(msg => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.text
    }));
  }, [messages]);

  /**
   * Export current session
   */
  const exportSession = useCallback(async () => {
    if (!sessionId) {
      setError('No active session to export');
      return null;
    }

    try {
      setError(null);
      const exported = await api.chat.exportSession(sessionId);
      return exported;
    } catch (err) {
      setError(err.message);
      console.error('Error exporting session:', err);
      throw err;
    }
  }, [sessionId]);

  /**
   * Download session as text file
   */
  const downloadSessionAsText = useCallback(async () => {
    if (!sessionId) {
      setError('No active session to download');
      return;
    }

    try {
      setError(null);
      const data = await api.chat.downloadSessionTxt(sessionId);
      
      // Create blob and download
      const blob = new Blob([data.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${data.title}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      return true;
    } catch (err) {
      setError(err.message);
      console.error('Error downloading session:', err);
      throw err;
    }
  }, [sessionId]);

  /**
   * Get total tokens used in current session
   */
  const getTotalTokens = useCallback(() => {
    return messages.reduce((sum, msg) => sum + (msg.tokensUsed || 0), 0);
  }, [messages]);

  return {
    // State
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

    // Utilities
    estimateTokens,
    getConversationHistory,
    exportSession,
    downloadSessionAsText,
    getTotalTokens
  };
};

export default useChatPersistence;