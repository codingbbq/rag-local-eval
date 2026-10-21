"""
Chat Persistence Service: Store and retrieve chat conversations
Supports multiple backends: SQLite, JSON files, and in-memory
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a single chat message"""
    id: str
    content: str
    role: str  # "user" or "assistant"
    timestamp: str
    tokens_used: int = 0
    is_on_topic: bool = True
    source_document_count: int = 0
    request_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChatSession:
    """Represents a complete chat session"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessage]
    total_tokens: int = 0
    message_count: int = 0
    is_archived: bool = False
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "total_tokens": self.total_tokens,
            "message_count": self.message_count,
            "is_archived": self.is_archived,
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "messages": [msg.to_dict() for msg in self.messages]
        }


class ChatStorageBackend(ABC):
    """Abstract base class for chat storage backends"""
    
    @abstractmethod
    async def save_session(self, session: ChatSession) -> bool:
        """Save a complete chat session"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a complete chat session"""
        pass
    
    @abstractmethod
    async def get_all_sessions(self, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """Get all sessions (paginated)"""
        pass
    
    @abstractmethod
    async def add_message(self, session_id: str, message: ChatMessage) -> bool:
        """Add a message to existing session"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        pass
    
    @abstractmethod
    async def search_sessions(self, query: str) -> List[ChatSession]:
        """Search sessions by query"""
        pass
    
    @abstractmethod
    async def clear_all(self) -> bool:
        """Clear all sessions"""
        pass


class SQLiteBackend(ChatStorageBackend):
    """SQLite-based persistent storage"""
    
    def __init__(self, db_path: str = "backend/data/chat_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    total_tokens INTEGER DEFAULT 0,
                    message_count INTEGER DEFAULT 0,
                    is_archived BOOLEAN DEFAULT 0,
                    tags TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    role TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tokens_used INTEGER DEFAULT 0,
                    is_on_topic BOOLEAN DEFAULT 1,
                    source_document_count INTEGER DEFAULT 0,
                    request_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_created 
                ON sessions(created_at DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id)
            """)
            
            conn.commit()
        logger.info(f"SQLite database initialized at {self.db_path}")
    
    async def save_session(self, session: ChatSession) -> bool:
        """Save session and all messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Save session metadata
                conn.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_id, title, created_at, updated_at, total_tokens, message_count, is_archived, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.title,
                    session.created_at,
                    session.updated_at,
                    session.total_tokens,
                    len(session.messages),
                    session.is_archived,
                    json.dumps(session.tags or []),
                    json.dumps(session.metadata or {})
                ))
                
                # Save messages
                for msg in session.messages:
                    conn.execute("""
                        INSERT OR REPLACE INTO messages
                        (id, session_id, content, role, timestamp, tokens_used, is_on_topic, source_document_count, request_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        msg.id,
                        session.session_id,
                        msg.content,
                        msg.role,
                        msg.timestamp,
                        msg.tokens_used,
                        msg.is_on_topic,
                        msg.source_document_count,
                        msg.request_id
                    ))
                
                conn.commit()
            
            logger.info(f"Saved session {session.session_id} with {len(session.messages)} messages")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve session with all messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get session
                session_row = conn.execute(
                    "SELECT * FROM sessions WHERE session_id = ?",
                    (session_id,)
                ).fetchone()
                
                if not session_row:
                    return None
                
                # Get messages
                message_rows = conn.execute(
                    "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                    (session_id,)
                ).fetchall()
                
                messages = [
                    ChatMessage(
                        id=msg["id"],
                        content=msg["content"],
                        role=msg["role"],
                        timestamp=msg["timestamp"],
                        tokens_used=msg["tokens_used"],
                        is_on_topic=bool(msg["is_on_topic"]),
                        source_document_count=msg["source_document_count"],
                        request_id=msg["request_id"]
                    )
                    for msg in message_rows
                ]
                
                session = ChatSession(
                    session_id=session_row["session_id"],
                    title=session_row["title"],
                    created_at=session_row["created_at"],
                    updated_at=session_row["updated_at"],
                    total_tokens=session_row["total_tokens"],
                    message_count=session_row["message_count"],
                    is_archived=bool(session_row["is_archived"]),
                    tags=json.loads(session_row["tags"]),
                    metadata=json.loads(session_row["metadata"]),
                    messages=messages
                )
                
                logger.info(f"Retrieved session {session_id}")
                return session
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            return None
    
    async def get_all_sessions(self, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """Get all sessions paginated"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                rows = conn.execute("""
                    SELECT * FROM sessions 
                    ORDER BY updated_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()
                
                sessions = []
                for row in rows:
                    # Get messages for this session
                    message_rows = conn.execute(
                        "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                        (row["session_id"],)
                    ).fetchall()
                    
                    messages = [
                        ChatMessage(
                            id=msg["id"],
                            content=msg["content"],
                            role=msg["role"],
                            timestamp=msg["timestamp"],
                            tokens_used=msg["tokens_used"],
                            is_on_topic=bool(msg["is_on_topic"]),
                            source_document_count=msg["source_document_count"],
                            request_id=msg["request_id"]
                        )
                        for msg in message_rows
                    ]
                    
                    session = ChatSession(
                        session_id=row["session_id"],
                        title=row["title"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        total_tokens=row["total_tokens"],
                        message_count=row["message_count"],
                        is_archived=bool(row["is_archived"]),
                        tags=json.loads(row["tags"]),
                        metadata=json.loads(row["metadata"]),
                        messages=messages
                    )
                    sessions.append(session)
                
                logger.info(f"Retrieved {len(sessions)} sessions")
                return sessions
        except Exception as e:
            logger.error(f"Error retrieving sessions: {e}")
            return []
    
    async def add_message(self, session_id: str, message: ChatMessage) -> bool:
        """Add message to session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO messages
                    (id, session_id, content, role, timestamp, tokens_used, is_on_topic, source_document_count, request_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id,
                    session_id,
                    message.content,
                    message.role,
                    message.timestamp,
                    message.tokens_used,
                    message.is_on_topic,
                    message.source_document_count,
                    message.request_id
                ))
                
                # Update session timestamp
                conn.execute(
                    "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                    (datetime.utcnow().isoformat(), session_id)
                )
                
                conn.commit()
            logger.info(f"Added message to session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session and messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
            logger.info(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    async def search_sessions(self, query: str) -> List[ChatSession]:
        """Search sessions by title or content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                rows = conn.execute("""
                    SELECT DISTINCT s.* FROM sessions s
                    WHERE s.title LIKE ? OR s.session_id IN (
                        SELECT session_id FROM messages WHERE content LIKE ?
                    )
                    ORDER BY s.updated_at DESC
                """, (f"%{query}%", f"%{query}%")).fetchall()
                
                sessions = []
                for row in rows:
                    message_rows = conn.execute(
                        "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                        (row["session_id"],)
                    ).fetchall()
                    
                    messages = [
                        ChatMessage(
                            id=msg["id"],
                            content=msg["content"],
                            role=msg["role"],
                            timestamp=msg["timestamp"],
                            tokens_used=msg["tokens_used"],
                            is_on_topic=bool(msg["is_on_topic"]),
                            source_document_count=msg["source_document_count"],
                            request_id=msg["request_id"]
                        )
                        for msg in message_rows
                    ]
                    
                    session = ChatSession(
                        session_id=row["session_id"],
                        title=row["title"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        total_tokens=row["total_tokens"],
                        message_count=row["message_count"],
                        is_archived=bool(row["is_archived"]),
                        tags=json.loads(row["tags"]),
                        metadata=json.loads(row["metadata"]),
                        messages=messages
                    )
                    sessions.append(session)
                
                logger.info(f"Found {len(sessions)} sessions matching '{query}'")
                return sessions
        except Exception as e:
            logger.error(f"Error searching sessions: {e}")
            return []
    
    async def clear_all(self) -> bool:
        """Delete all sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM messages")
                conn.execute("DELETE FROM sessions")
                conn.commit()
            logger.info("Cleared all sessions")
            return True
        except Exception as e:
            logger.error(f"Error clearing sessions: {e}")
            return False


class JSONBackend(ChatStorageBackend):
    """JSON file-based storage (simpler, no database needed)"""
    
    def __init__(self, data_dir: str = "backend/data/chat_sessions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"JSON storage initialized at {self.data_dir}")
    
    def _get_session_path(self, session_id: str) -> Path:
        return self.data_dir / f"{session_id}.json"
    
    async def save_session(self, session: ChatSession) -> bool:
        """Save session to JSON file"""
        try:
            path = self._get_session_path(session.session_id)
            with open(path, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            logger.info(f"Saved session {session.session_id} to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Load session from JSON file"""
        try:
            path = self._get_session_path(session_id)
            if not path.exists():
                return None
            
            with open(path, 'r') as f:
                data = json.load(f)
            
            messages = [
                ChatMessage(**msg) for msg in data["messages"]
            ]
            
            session = ChatSession(
                session_id=data["session_id"],
                title=data["title"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                total_tokens=data["total_tokens"],
                message_count=data["message_count"],
                is_archived=data.get("is_archived", False),
                tags=data.get("tags", []),
                metadata=data.get("metadata", {}),
                messages=messages
            )
            
            logger.info(f"Retrieved session {session_id}")
            return session
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            return None
    
    async def get_all_sessions(self, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """Get all sessions from JSON files"""
        try:
            json_files = sorted(
                self.data_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            sessions = []
            for json_file in json_files[offset:offset + limit]:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                messages = [ChatMessage(**msg) for msg in data["messages"]]
                session = ChatSession(
                    session_id=data["session_id"],
                    title=data["title"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    total_tokens=data["total_tokens"],
                    message_count=data["message_count"],
                    is_archived=data.get("is_archived", False),
                    tags=data.get("tags", []),
                    metadata=data.get("metadata", {}),
                    messages=messages
                )
                sessions.append(session)
            
            logger.info(f"Retrieved {len(sessions)} sessions")
            return sessions
        except Exception as e:
            logger.error(f"Error retrieving sessions: {e}")
            return []
    
    async def add_message(self, session_id: str, message: ChatMessage) -> bool:
        """Add message and resave session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False
            
            session.messages.append(message)
            session.updated_at = datetime.utcnow().isoformat()
            
            return await self.save_session(session)
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session JSON file"""
        try:
            path = self._get_session_path(session_id)
            if path.exists():
                path.unlink()
            logger.info(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    async def search_sessions(self, query: str) -> List[ChatSession]:
        """Search sessions by title or content"""
        try:
            matching_sessions = []
            
            for json_file in self.data_dir.glob("*.json"):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Search in title and messages
                title_match = query.lower() in data["title"].lower()
                content_match = any(
                    query.lower() in msg["content"].lower()
                    for msg in data["messages"]
                )
                
                if title_match or content_match:
                    messages = [ChatMessage(**msg) for msg in data["messages"]]
                    session = ChatSession(
                        session_id=data["session_id"],
                        title=data["title"],
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        total_tokens=data["total_tokens"],
                        message_count=data["message_count"],
                        is_archived=data.get("is_archived", False),
                        tags=data.get("tags", []),
                        metadata=data.get("metadata", {}),
                        messages=messages
                    )
                    matching_sessions.append(session)
            
            logger.info(f"Found {len(matching_sessions)} sessions matching '{query}'")
            return matching_sessions
        except Exception as e:
            logger.error(f"Error searching sessions: {e}")
            return []
    
    async def clear_all(self) -> bool:
        """Delete all session files"""
        try:
            for json_file in self.data_dir.glob("*.json"):
                json_file.unlink()
            logger.info("Cleared all sessions")
            return True
        except Exception as e:
            logger.error(f"Error clearing sessions: {e}")
            return False


class ChatPersistenceService:
    """
    High-level chat persistence service
    Abstracts away storage backend
    """
    
    def __init__(self, backend: ChatStorageBackend = None):
        """
        Initialize with backend (default: SQLite)
        
        Args:
            backend: Storage backend (SQLiteBackend, JSONBackend, or custom)
        """
        self.backend = backend or SQLiteBackend()
        logger.info(f"Chat persistence initialized with {type(self.backend).__name__}")
    
    async def create_session(self, title: str, tags: List[str] = None, 
                           metadata: Dict[str, Any] = None) -> ChatSession:
        """Create new chat session"""
        session_id = hashlib.md5(
            f"{title}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        now = datetime.utcnow().isoformat()
        session = ChatSession(
            session_id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
            messages=[],
            tags=tags or [],
            metadata=metadata or {}
        )
        
        await self.backend.save_session(session)
        logger.info(f"Created new session: {session_id}")
        return session
    
    async def add_message_to_session(self, session_id: str, content: str, role: str,
                                    tokens_used: int = 0, is_on_topic: bool = True,
                                    source_document_count: int = 0, request_id: str = "") -> bool:
        """Add message to session"""
        msg_id = hashlib.md5(
            f"{session_id}{content}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        message = ChatMessage(
            id=msg_id,
            content=content,
            role=role,
            timestamp=datetime.utcnow().isoformat(),
            tokens_used=tokens_used,
            is_on_topic=is_on_topic,
            source_document_count=source_document_count,
            request_id=request_id
        )
        
        return await self.backend.add_message(session_id, message)
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session with all messages"""
        return await self.backend.get_session(session_id)
    
    async def get_all_sessions(self, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """Get all sessions"""
        return await self.backend.get_all_sessions(limit, offset)
    
    async def search_sessions(self, query: str) -> List[ChatSession]:
        """Search sessions"""
        return await self.backend.search_sessions(query)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return await self.backend.delete_session(session_id)
    
    async def clear_all(self) -> bool:
        """Clear all sessions"""
        return await self.backend.clear_all()