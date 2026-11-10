const API_BASE = 'http://localhost:8000/api/v1';

// RAG QUERIES
export const query = async (userQuery, conversationHistory = []) => {
    const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: userQuery,
            conversation_history: conversationHistory,
            top_k: 5
        })
    });
    if (!response.ok) throw new Error(`Query failed: ${response.statusText}`);
    return await response.json();
};

export const uploadDocuments = async (files) => {
    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }
    const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
    });
    if (!response.ok) throw new Error(`Upload failed: ${response.statusText}`);
    return await response.json();
};

export const getConversationHistory = async () => {
    const response = await fetch(`${API_BASE}/conversation/history`);
    if (!response.ok) throw new Error(`Failed to get history: ${response.statusText}`);
    return await response.json();
};

// CHAT PERSISTENCE - SESSIONS
export const createSession = async (data) => {
    const title = typeof data === 'string' ? data : (data?.title || `Chat ${new Date().toLocaleDateString()}`);

    const params = new URLSearchParams();
    params.append('title', title);

    const response = await fetch(`${API_BASE}/chat/session/create?${params.toString()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) throw new Error(`Failed to create session: ${response.statusText}`);
    const result = await response.json();

    // Handle both response formats
    return result.data || result;
};

export const listSessions = async (page = 1, limit = 50) => {
    const response = await fetch(`${API_BASE}/chat/sessions/list?page=${page}&limit=${limit}`);
    if (!response.ok) throw new Error(`Failed to list sessions: ${response.statusText}`);
    return await response.json();
};

export const getSession = async (sessionId) => {
    const response = await fetch(`${API_BASE}/chat/session/${sessionId}`);
    if (!response.ok) throw new Error(`Failed to get session: ${response.statusText}`);
    return await response.json();
};

export const addMessageToSession = async (sessionId, message) => {
    const params = new URLSearchParams();
    params.append('session_id', sessionId);
    params.append('content', message.content);
    params.append('role', message.type === 'user' ? 'user' : 'assistant');
    params.append('tokens_used', message.tokensUsed || 0);
    params.append('is_on_topic', message.isOnTopic !== undefined ? message.isOnTopic : true);
    params.append('source_document_count', message.sourceDocumentCount || 0);

    const response = await fetch(`${API_BASE}/chat/message/add?${params.toString()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) throw new Error(`Failed to add message: ${response.statusText}`);
    return await response.json();
};

export const deleteSession = async (sessionId) => {
    const response = await fetch(`${API_BASE}/chat/session/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) throw new Error(`Failed to delete session: ${response.statusText}`);
    return await response.json();
};

export const downloadSessionAsText = async (sessionId) => {
    const response = await fetch(`${API_BASE}/chat/session/${sessionId}/download-txt`);
    if (!response.ok) throw new Error(`Failed to download session: ${response.statusText}`);
    return await response.text();
};

export const exportSession = async (sessionId) => {
    const response = await fetch(`${API_BASE}/chat/session/${sessionId}/export`);
    if (!response.ok) throw new Error(`Failed to export session: ${response.statusText}`);
    return await response.json();
};

export const getChatStatistics = async () => {
    const response = await fetch(`${API_BASE}/chat/statistics`);
    if (!response.ok) throw new Error(`Failed to get statistics: ${response.statusText}`);
    return await response.json();
};

export const checkHealth = async () => {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return await response.json();
};

export default {
    query,
    uploadDocuments,
    getConversationHistory,
    createSession,
    listSessions,
    getSession,
    addMessageToSession,
    deleteSession,
    downloadSessionAsText,
    exportSession,
    getChatStatistics,
    checkHealth
};