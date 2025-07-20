from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CodeRequest(BaseModel):
    code: str
    language: str = "javascript"
    context: str = ""
    chat_id: Optional[str] = None

class ChatMessage(BaseModel):
    id: str
    chat_id: str
    content: str
    is_user: bool
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class Chat(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []

class CodeResponse(BaseModel):
    corrected_code: str
    explanation: str
    visualization_html: str
    suggestions: List[str]
    warnings: List[str]

class ChatResponse(BaseModel):
    chat_id: str
    message: ChatMessage
    ai_response: Optional[CodeResponse] = None

class QueryRequest(BaseModel):
    query: str
    system_prompt: str