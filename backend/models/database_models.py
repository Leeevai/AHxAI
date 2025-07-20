from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessageDB(BaseModel):
    id: str
    chat_id: str
    content: str
    is_user: bool
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatDB(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class CodeProjectDB(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    language: str
    code_content: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None

class CodeAnalysisDB(BaseModel):
    id: str
    project_id: str
    original_code: str
    corrected_code: str
    explanation: str
    suggestions: List[str]
    warnings: List[str]
    analysis_type: str
    created_at: datetime

class UserSessionDB(BaseModel):
    id: str
    session_token: str
    user_data: Dict[str, Any]
    created_at: datetime
    expires_at: datetime