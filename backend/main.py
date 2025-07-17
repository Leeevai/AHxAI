from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import os
from datetime import datetime
import uuid
import json
from contextlib import asynccontextmanager

# Database models (using in-memory storage for simplicity)
# In production, use PostgreSQL, MongoDB, etc.
chats_db = {}
messages_db = {}

# Pydantic models
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

# Initialize Gemini
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Coding AI Agent API",
    description="Backend API for AI-powered coding assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini client
model = genai.GenerativeModel('gemini-pro')

def create_analysis_prompt(code: str, language: str, context: str) -> str:
    return f"""
    You are an expert code analyst. Analyze the following {language} code and provide:
    
    1. CORRECTED_CODE: Improved version of the code with best practices
    2. EXPLANATION: Clear explanation of what the code does and improvements made
    3. VISUALIZATION_HTML: HTML/CSS visualization that represents the code's functionality, data structures, or algorithm flow
    4. SUGGESTIONS: List of specific improvement suggestions
    5. WARNINGS: List of potential issues or performance concerns
    
    Context: {context}
    
    Code to analyze:
    ```{language}
    {code}
    ```
    
    Please format your response as JSON with the following structure:
    {{
        "corrected_code": "improved code here",
        "explanation": "detailed explanation here",
        "visualization_html": "complete HTML with embedded CSS for visualization",
        "suggestions": ["suggestion 1", "suggestion 2", ...],
        "warnings": ["warning 1", "warning 2", ...]
    }}
    """

async def analyze_code_with_gemini(code: str, language: str, context: str) -> CodeResponse:
    try:
        prompt = create_analysis_prompt(code, language, context)
        response = model.generate_content(prompt)
        
        # Parse JSON response
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            result = {
                "corrected_code": code,
                "explanation": response.text,
                "visualization_html": "<div>Visualization not available</div>",
                "suggestions": [],
                "warnings": []
            }
        
        return CodeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Coding AI Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/chats", response_model=Chat)
async def create_chat():
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())
    chat = Chat(
        id=chat_id,
        title="New Chat",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    chats_db[chat_id] = chat
    return chat

@app.get("/api/chats", response_model=List[Chat])
async def get_chats():
    """Get all chat sessions"""
    return list(chats_db.values())

@app.get("/api/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str):
    """Get a specific chat session"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = chats_db[chat_id]
    # Add messages to chat
    chat.messages = [msg for msg in messages_db.values() if msg.chat_id == chat_id]
    return chat

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat session"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete chat and its messages
    del chats_db[chat_id]
    messages_to_delete = [msg_id for msg_id, msg in messages_db.items() if msg.chat_id == chat_id]
    for msg_id in messages_to_delete:
        del messages_db[msg_id]
    
    return {"message": "Chat deleted successfully"}

@app.post("/api/analyze", response_model=ChatResponse)
async def analyze_code(request: CodeRequest):
    """Analyze code and return results"""
    
    # Create or get chat
    chat_id = request.chat_id
    if not chat_id:
        chat = await create_chat()
        chat_id = chat.id
    elif chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Create user message
    user_msg_id = str(uuid.uuid4())
    user_message = ChatMessage(
        id=user_msg_id,
        chat_id=chat_id,
        content=f"Analyze this {request.language} code: {request.code[:100]}...",
        is_user=True,
        timestamp=datetime.now(),
        metadata={"code": request.code, "language": request.language, "context": request.context}
    )
    messages_db[user_msg_id] = user_message
    
    # Analyze code with Gemini
    ai_response = await analyze_code_with_gemini(request.code, request.language, request.context)
    
    # Create AI response message
    ai_msg_id = str(uuid.uuid4())
    ai_message = ChatMessage(
        id=ai_msg_id,
        chat_id=chat_id,
        content="I've analyzed your code and provided improvements, explanations, and visualizations.",
        is_user=False,
        timestamp=datetime.now(),
        metadata=ai_response.dict()
    )
    messages_db[ai_msg_id] = ai_message
    
    # Update chat title and timestamp
    if chat_id in chats_db:
        chats_db[chat_id].title = f"Code Analysis - {request.language}"
        chats_db[chat_id].updated_at = datetime.now()
    
    return ChatResponse(
        chat_id=chat_id,
        message=ai_message,
        ai_response=ai_response
    )

@app.get("/api/chats/{chat_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(chat_id: str):
    """Get messages for a specific chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = [msg for msg in messages_db.values() if msg.chat_id == chat_id]
    return sorted(messages, key=lambda x: x.timestamp)

@app.get("/api/visualization/{message_id}", response_class=HTMLResponse)
async def get_visualization(message_id: str):
    """Get HTML visualization for a specific message"""
    if message_id not in messages_db:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = messages_db[message_id]
    if not message.metadata or "visualization_html" not in message.metadata:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    return HTMLResponse(content=message.metadata["visualization_html"])

@app.post("/api/chats/{chat_id}/messages", response_model=ChatMessage)
async def send_message(chat_id: str, message: dict):
    """Send a message to a chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    msg_id = str(uuid.uuid4())
    chat_message = ChatMessage(
        id=msg_id,
        chat_id=chat_id,
        content=message["content"],
        is_user=message.get("is_user", True),
        timestamp=datetime.now()
    )
    messages_db[msg_id] = chat_message
    
    # Update chat timestamp
    chats_db[chat_id].updated_at = datetime.now()
    
    return chat_message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)