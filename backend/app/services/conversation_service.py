from typing import List, Dict
from datetime import datetime
from app.utils.logger import logger
import tiktoken

debug_logger = logger.get_logger(__name__)

class ConversationMessage:
    """Represents a single message in conversation"""
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class ConversationService:
    """Manages conversation history and context"""
    
    def __init__(self, max_history_turns: int = 5):
        """
        Initialize conversation service
        
        Args:
            max_history_turns: Number of previous Q&A pairs to keep
        """
        self.history: List[ConversationMessage] = []
        self.max_history_turns = max_history_turns
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.max_tokens = 2000  # Safe limit for context
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        msg = ConversationMessage(role, content)
        self.history.append(msg)
        debug_logger.info(f"Added {role} message: {len(content)} chars")
    
    def get_history_text(self, include_last_n_turns: int = None) -> str:
        """
        Get conversation history as formatted text
        
        Args:
            include_last_n_turns: Number of turns to include (default: max_history_turns)
            
        Returns:
            Formatted conversation history
        """
        n_turns = include_last_n_turns or self.max_history_turns
        
        # Get last n complete turns (user + assistant pairs)
        turns = []
        for i in range(len(self.history) - 1, -1, -1):
            if len(turns) >= n_turns * 2:  # Each turn is 2 messages
                break
            turns.insert(0, self.history[i])
        
        if not turns:
            return ""
        
        # Format as text
        history_text = "Previous conversation:\n"
        current_turn = []
        
        for msg in turns:
            if msg.role == 'user':
                current_turn = [msg.content]
            else:
                if current_turn:
                    history_text += f"Q: {current_turn[0]}\n"
                history_text += f"A: {msg.content}\n\n"
        
        return history_text
    
    def get_token_count(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def should_trim_history(self, new_content: str, context: str) -> bool:
        """
        Check if we should trim history due to token limits
        
        Args:
            new_content: New query/answer
            context: Retrieved context from FAISS
            
        Returns:
            True if history should be trimmed
        """
        history_tokens = self.get_token_count(self.get_history_text())
        context_tokens = self.get_token_count(context)
        new_tokens = self.get_token_count(new_content)
        
        total = history_tokens + context_tokens + new_tokens
        
        if total > self.max_tokens:
            debug_logger.warning(
                f"⚠️ Token limit exceeded: {total} > {self.max_tokens}"
            )
            return True
        
        return False
    
    def trim_history(self):
        """Remove oldest message from history"""
        if len(self.history) > 0:
            removed = self.history.pop(0)
            debug_logger.info(f"Trimmed oldest message: {removed.role}")
    
    def clear_history(self):
        """Clear all history"""
        self.history.clear()
        debug_logger.info("Cleared conversation history")
    
    def get_conversation_context(self, new_query: str, retrieved_context: str) -> str:
        """
        Build full context for LLM including history
        
        Args:
            new_query: Current user query
            retrieved_context: Context from FAISS
            
        Returns:
            Full context string
        """
        history_text = self.get_history_text()
        
        # Trim history if needed
        while self.should_trim_history(new_query, retrieved_context + history_text):
            self.trim_history()
            history_text = self.get_history_text()
        
        full_context = f"""{history_text}

Retrieved Context:
{retrieved_context}

Current Question: {new_query}"""
        
        return full_context
    
    def export_history(self) -> List[Dict]:
        """Export history as list of dicts"""
        return [msg.to_dict() for msg in self.history]

# Global instance
conversation_service = ConversationService()
