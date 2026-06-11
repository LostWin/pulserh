from pydantic import BaseModel
from typing import Optional, List, Literal

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: List[str]

class FeedbackRequest(BaseModel):
    rating: Literal["useful", "useless"]
    comment: Optional[str] = None