from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    context: Optional[str] = Field(None, description="Conversation context")

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class ConversationStarterRequest(BaseModel):
    target_user_id: str = Field(..., description="ID of user to generate starter for")

class ConversationStarterResponse(BaseModel):
    starter: str
    target_user: str
    timestamp: str