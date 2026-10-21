/**
 * API Client Service
 * Centralized place for all API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  // ============================================
  // CHAT & QUERY ENDPOINTS
  // ============================================
  
  /**
   * Send a query to the RAG system
   */
  query: async (question, conversationHistory = []) => {
    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: question,
          conversation_history: conversationHistory
        })
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error querying RAG:', error);
      throw error;
    }
  },

  // ============================================
  // CHAT SESSION ENDPOINTS
  // ============================================

  /**
   * Create a new chat session
   */
  chat: {
    createSession: async (title = null, tags = []) => {
      try {
        const sessionTitle = title || `Chat - ${new Date().toLocaleString()}`;
        const params = new URLSearchParams({
          title: sessionTitle,
          ...tags.reduce((acc, tag, idx) => ({ ...acc, [`tags`]: tag }), {})
        });

        const response = await fetch(`${API_BASE_URL}/chat/session/create?${params}`, {
          method: 'POST'
        });

        if (!response.ok) {
          throw new Error(`Create session failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error creating session:', error);
        throw error;
      }
    },

    /**
     * Get a complete session with all messages
     */
    getSession: async (sessionId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/session/${sessionId}`);

        if (!response.ok) {
          throw new Error(`Get session failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error getting session:', error);
        throw error;
      }
    },

    /**
     * Add a message to a session
     */
    addMessage: async (sessionId, content, role, options = {}) => {
      try {
        const {
          tokensUsed = 0,
          isOnTopic = true,
          sourceDocumentCount = 0,
          requestId = ''
        } = options;

        const params = new URLSearchParams({
          session_id: sessionId,
          content: content,
          role: role,
          tokens_used: tokensUsed,
          is_on_topic: isOnTopic,
          source_document_count: sourceDocumentCount,
          request_id: requestId
        });

        const response = await fetch(`${API_BASE_URL}/chat/message/add?${params}`, {
          method: 'POST'
        });

        if (!response.ok) {
          throw new Error(`Add message failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error adding message:', error);
        throw error;
      }
    },

    /**
     * List all sessions (paginated)
     */
    listSessions: async (limit = 20, offset = 0) => {
      try {
        const params = new URLSearchParams({
          limit: limit,
          offset: offset
        });

        const response = await fetch(`${API_BASE_URL}/chat/sessions/list?${params}`);

        if (!response.ok) {
          throw new Error(`List sessions failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error listing sessions:', error);
        throw error;
      }
    },

    /**
     * Search sessions by query
     */
    searchSessions: async (query) => {
      try {
        const params = new URLSearchParams({
          query: query
        });

        const response = await fetch(`${API_BASE_URL}/chat/sessions/search?${params}`);

        if (!response.ok) {
          throw new Error(`Search sessions failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error searching sessions:', error);
        throw error;
      }
    },

    /**
     * Delete a session
     */
    deleteSession: async (sessionId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/session/${sessionId}`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          throw new Error(`Delete session failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error deleting session:', error);
        throw error;
      }
    },

    /**
     * Export session as JSON
     */
    exportSession: async (sessionId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/session/${sessionId}/export`);

        if (!response.ok) {
          throw new Error(`Export session failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error exporting session:', error);
        throw error;
      }
    },

    /**
     * Download session as text
     */
    downloadSessionTxt: async (sessionId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/session/${sessionId}/download-txt`);

        if (!response.ok) {
          throw new Error(`Download session failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error downloading session:', error);
        throw error;
      }
    },

    /**
     * Get chat statistics
     */
    getStatistics: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/statistics`);

        if (!response.ok) {
          throw new Error(`Get statistics failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.data;
      } catch (error) {
        console.error('Error getting statistics:', error);
        throw error;
      }
    }
  },

  // ============================================
  // UPLOAD ENDPOINTS
  // ============================================

  /**
   * Upload files
   */
  upload: async (files) => {
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading files:', error);
      throw error;
    }
  },

  /**
   * Process uploaded files
   */
  processUploads: async (chunkSize = 1000, chunkOverlap = 200, retrievalK = 5) => {
    try {
      const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          chunk_size: chunkSize,
          chunk_overlap: chunkOverlap,
          retrieval_k: retrievalK
        })
      });

      if (!response.ok) {
        throw new Error(`Process failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error processing uploads:', error);
      throw error;
    }
  },

  /**
   * Clear uploads
   */
  clearUploads: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/uploads/clear`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Clear uploads failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error clearing uploads:', error);
      throw error;
    }
  },

  // ============================================
  // CONVERSATION HISTORY ENDPOINTS
  // ============================================

  /**
   * Clear conversation history
   */
  clearConversationHistory: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversation/clear`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Clear history failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error clearing conversation history:', error);
      throw error;
    }
  },

  /**
   * Get conversation history
   */
  getConversationHistory: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversation/history`);

      if (!response.ok) {
        throw new Error(`Get history failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation history:', error);
      throw error;
    }
  },

  // ============================================
  // HEALTH CHECK
  // ============================================

  /**
   * Check backend health
   */
  health: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
};

export default api;
