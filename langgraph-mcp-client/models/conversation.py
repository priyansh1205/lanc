from typing import List
from dataclasses import dataclass, field
from models.message import Message

@dataclass
class Conversation:
    messages: List[Message] = field(default_factory=list)
    conversation_id: str = ""
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """Add a message to the conversation"""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
    
    def clear(self):
        """Clear conversation history"""
        self.messages.clear()
    
    def to_langgraph_format(self) -> dict:
        """Convert to LangGraph compatible format"""
        return {
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    def get_context_summary(self, last_n: int = 4) -> str:
        """Get a summary of recent conversation context"""
        if len(self.messages) == 0:
            return "No previous context"
        
        recent_messages = self.messages[-last_n:]
        exchanges = len(recent_messages) // 2
        return f"Context: {exchanges} previous exchanges"
