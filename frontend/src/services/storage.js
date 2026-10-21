/**
 * Storage Helper
 * Manages browser localStorage for chat data
 */

const STORAGE_KEYS = {
  CURRENT_SESSION_ID: 'rag_current_session_id',
  SESSION_HISTORY: 'rag_session_history',
  CURRENT_MESSAGES: 'rag_current_messages'
};

export const storage = {
  // ============================================
  // SESSION ID MANAGEMENT
  // ============================================

  /**
   * Save current session ID
   */
  setCurrentSessionId: (sessionId) => {
    try {
      localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION_ID, sessionId);
      return true;
    } catch (error) {
      console.error('Error saving session ID:', error);
      return false;
    }
  },

  /**
   * Get current session ID
   */
  getCurrentSessionId: () => {
    try {
      return localStorage.getItem(STORAGE_KEYS.CURRENT_SESSION_ID);
    } catch (error) {
      console.error('Error getting session ID:', error);
      return null;
    }
  },

  /**
   * Clear current session ID
   */
  clearCurrentSessionId: () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION_ID);
      return true;
    } catch (error) {
      console.error('Error clearing session ID:', error);
      return false;
    }
  },

  // ============================================
  // SESSION HISTORY MANAGEMENT
  // ============================================

  /**
   * Add session to history (quick access)
   */
  addToSessionHistory: (session) => {
    try {
      const history = storage.getSessionHistory();
      const exists = history.some(s => s.session_id === session.session_id);
      
      if (!exists) {
        history.unshift(session);
        // Keep only last 10 sessions in memory
        if (history.length > 10) {
          history.pop();
        }
        localStorage.setItem(STORAGE_KEYS.SESSION_HISTORY, JSON.stringify(history));
      }
      return true;
    } catch (error) {
      console.error('Error adding to session history:', error);
      return false;
    }
  },

  /**
   * Get session history from localStorage
   */
  getSessionHistory: () => {
    try {
      const history = localStorage.getItem(STORAGE_KEYS.SESSION_HISTORY);
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error('Error getting session history:', error);
      return [];
    }
  },

  /**
   * Clear session history
   */
  clearSessionHistory: () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.SESSION_HISTORY);
      return true;
    } catch (error) {
      console.error('Error clearing session history:', error);
      return false;
    }
  },

  /**
   * Remove specific session from history
   */
  removeFromSessionHistory: (sessionId) => {
    try {
      const history = storage.getSessionHistory();
      const filtered = history.filter(s => s.session_id !== sessionId);
      localStorage.setItem(STORAGE_KEYS.SESSION_HISTORY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error removing from session history:', error);
      return false;
    }
  },

  // ============================================
  // TEMPORARY MESSAGE CACHE
  // ============================================

  /**
   * Cache current messages (for quick restore on reload)
   */
  setCacheMessages: (messages) => {
    try {
      localStorage.setItem(STORAGE_KEYS.CURRENT_MESSAGES, JSON.stringify(messages));
      return true;
    } catch (error) {
      console.error('Error caching messages:', error);
      return false;
    }
  },

  /**
   * Get cached messages
   */
  getCachedMessages: () => {
    try {
      const messages = localStorage.getItem(STORAGE_KEYS.CURRENT_MESSAGES);
      return messages ? JSON.parse(messages) : [];
    } catch (error) {
      console.error('Error getting cached messages:', error);
      return [];
    }
  },

  /**
   * Clear cached messages
   */
  clearCachedMessages: () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_MESSAGES);
      return true;
    } catch (error) {
      console.error('Error clearing cached messages:', error);
      return false;
    }
  },

  // ============================================
  // UTILITY FUNCTIONS
  // ============================================

  /**
   * Clear all storage
   */
  clearAll: () => {
    try {
      Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
      });
      return true;
    } catch (error) {
      console.error('Error clearing all storage:', error);
      return false;
    }
  },

  /**
   * Get storage size (for monitoring)
   */
  getStorageSize: () => {
    try {
      let size = 0;
      Object.values(STORAGE_KEYS).forEach(key => {
        const item = localStorage.getItem(key);
        if (item) {
          size += item.length;
        }
      });
      return size;
    } catch (error) {
      console.error('Error getting storage size:', error);
      return 0;
    }
  }
};

export default storage;
