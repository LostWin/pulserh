from pydantic import BaseModel
from typing import Optional, List, Literal, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: List[str] = []
    tokens_used: int = 0
    tool_results: List[dict] = []
    confidence: float = 0.0
    warning: Optional[str] = None

class StreamChunk(BaseModel):
    """Chunk SSE pour le streaming."""
    type: Literal["text", "source", "tool_call", "done"]
    content: Any

class ConversationSummary(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: int = 0

class FeedbackRequest(BaseModel):
    rating: Literal["useful", "useless"]
    comment: Optional[str] = None