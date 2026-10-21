"""
Chat Persistence API Routes
Endpoints for saving, loading, and managing chat sessions
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.chat_persistence_service import (
    ChatPersistenceService, ChatSession, ChatMessage,
    SQLiteBackend, JSONBackend
)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Initialize persistence service (using SQLite by default)
persistence_service = ChatPersistenceService(backend=SQLiteBackend())

# Optional: Use JSON backend instead
# persistence_service = ChatPersistenceService(backend=JSONBackend())


# ============================================
# SESSION MANAGEMENT
# ============================================

@router.post("/session/create")
async def create_session(
    title: str = Query(..., description="Session title"),
    tags: List[str] = Query(None, description="Optional tags"),
    metadata: dict = None
) -> dict:
    """
    Create a new chat session
    
    Returns:
    - session_id: Unique identifier for the session
    - title: Session title
    - created_at: Creation timestamp
    
    Example:
    POST /api/v1/chat/session/create?title=My%20First%20Chat&tags=tutorial&tags=learning
    """
    try:
        session = await persistence_service.create_session(
            title=title,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        return {
            "success": True,
            "data": {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at,
                "message": f"Session created successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> dict:
    """
    Get a complete chat session with all messages
    
    Returns:
    - All messages in chronological order
    - Session metadata
    - Statistics (total tokens, message count)
    
    Example:
    GET /api/v1/chat/session/abc123def456
    """
    try:
        session = await persistence_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "data": session.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/list")
async def list_sessions(
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
) -> dict:
    """
    Get paginated list of all sessions
    
    Returns:
    - Session summaries (without full message content)
    - Most recently updated first
    - Pagination info
    
    Example:
    GET /api/v1/chat/sessions/list?limit=10&offset=0
    """
    try:
        sessions = await persistence_service.get_all_sessions(limit, offset)
        
        return {
            "success": True,
            "data": {
                "total": len(sessions),
                "limit": limit,
                "offset": offset,
                "sessions": [
                    {
                        "session_id": s.session_id,
                        "title": s.title,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                        "message_count": s.message_count,
                        "total_tokens": s.total_tokens,
                        "tags": s.tags,
                        "is_archived": s.is_archived
                    }
                    for s in sessions
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/search")
async def search_sessions(
    query: str = Query(..., description="Search query")
) -> dict:
    """
    Search sessions by title or message content
    
    Returns:
    - Matching sessions
    - Ranked by relevance (most recent first)
    
    Example:
    GET /api/v1/chat/sessions/search?query=A/B%20testing
    """
    try:
        sessions = await persistence_service.search_sessions(query)
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results_count": len(sessions),
                "sessions": [
                    {
                        "session_id": s.session_id,
                        "title": s.title,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                        "message_count": s.message_count,
                        "tags": s.tags
                    }
                    for s in sessions
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MESSAGE MANAGEMENT
# ============================================

@router.post("/message/add")
async def add_message(
    session_id: str = Query(..., description="Session ID"),
    content: str = Query(..., description="Message content"),
    role: str = Query(..., description="Message role (user or assistant)"),
    tokens_used: int = Query(0, description="Tokens used for this message"),
    is_on_topic: bool = Query(True, description="Whether message is on-topic"),
    source_document_count: int = Query(0, description="Number of source documents"),
    request_id: str = Query("", description="Associated request ID")
) -> dict:
    """
    Add a message to a session
    
    Args:
        role: "user" or "assistant"
        tokens_used: Number of tokens used
        is_on_topic: Whether response was on-topic
        source_document_count: Documents retrieved for this message
    
    Example:
    POST /api/v1/chat/message/add
    ?session_id=abc123
    &content=What%20is%20A/B%20testing?
    &role=user
    &tokens_used=45
    """
    try:
        if role not in ["user", "assistant"]:
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")
        
        success = await persistence_service.add_message_to_session(
            session_id=session_id,
            content=content,
            role=role,
            tokens_used=tokens_used,
            is_on_topic=is_on_topic,
            source_document_count=source_document_count,
            request_id=request_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "message": "Message added successfully",
                "message_content_preview": content[:100]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SESSION OPERATIONS
# ============================================

@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict:
    """
    Delete a session and all its messages
    
    Example:
    DELETE /api/v1/chat/session/abc123def456
    """
    try:
        success = await persistence_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "data": {
                "message": f"Session {session_id} deleted successfully"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/clear")
async def clear_all_sessions() -> dict:
    """
    Clear all sessions and messages (DESTRUCTIVE)
    
    Warning: This cannot be undone!
    
    Example:
    DELETE /api/v1/chat/sessions/clear
    """
    try:
        success = await persistence_service.clear_all()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear sessions")
        
        return {
            "success": True,
            "data": {
                "message": "All sessions cleared successfully"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# EXPORT/IMPORT
# ============================================

@router.get("/session/{session_id}/export")
async def export_session(session_id: str) -> dict:
    """
    Export a session as JSON (for backup or sharing)
    
    Returns:
    - Complete session data in JSON format
    - Can be saved to file or shared
    
    Example:
    GET /api/v1/chat/session/abc123def456/export
    """
    try:
        session = await persistence_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "data": session.to_dict(),
            "export_info": {
                "format": "json",
                "exported_at": datetime.utcnow().isoformat(),
                "message_count": session.message_count
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/download-txt")
async def download_session_txt(session_id: str) -> dict:
    """
    Get session as plaintext (for copying to notes, etc.)
    
    Returns:
    - Formatted text version of chat
    - Easy to read and share
    
    Example:
    GET /api/v1/chat/session/abc123def456/download-txt
    """
    try:
        session = await persistence_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Format as text
        text_content = f"Chat Session: {session.title}\n"
        text_content += f"Created: {session.created_at}\n"
        text_content += f"Messages: {session.message_count}\n"
        text_content += f"Tokens Used: {session.total_tokens}\n"
        text_content += "=" * 80 + "\n\n"
        
        for msg in session.messages:
            role_label = "👤 User" if msg.role == "user" else "🤖 Assistant"
            text_content += f"{role_label} ({msg.timestamp}):\n"
            text_content += f"{msg.content}\n"
            if msg.tokens_used > 0:
                text_content += f"[Tokens: {msg.tokens_used}]\n"
            text_content += "\n"
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "title": session.title,
                "content": text_content,
                "format": "text/plain"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# STATISTICS
# ============================================

@router.get("/statistics")
async def get_statistics() -> dict:
    """
    Get overall chat statistics
    
    Returns:
    - Total sessions
    - Total messages
    - Average tokens per session
    - Most active sessions
    
    Example:
    GET /api/v1/chat/statistics
    """
    try:
        sessions = await persistence_service.get_all_sessions(limit=1000)
        
        total_messages = sum(s.message_count for s in sessions)
        total_tokens = sum(s.total_tokens for s in sessions)
        
        return {
            "success": True,
            "data": {
                "total_sessions": len(sessions),
                "total_messages": total_messages,
                "total_tokens_used": total_tokens,
                "average_messages_per_session": (
                    total_messages / len(sessions) if sessions else 0
                ),
                "average_tokens_per_session": (
                    total_tokens / len(sessions) if sessions else 0
                ),
                "most_active_sessions": [
                    {
                        "session_id": s.session_id,
                        "title": s.title,
                        "message_count": s.message_count,
                        "total_tokens": s.total_tokens
                    }
                    for s in sorted(sessions, key=lambda x: x.message_count, reverse=True)[:5]
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))