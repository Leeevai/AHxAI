# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import os
from datetime import datetime
import uuid
import asyncio
from contextlib import asynccontextmanager

# Pydantic models
class CodeRequest(BaseModel):
    code: str
    language: str
    prompt: str
    action: str  # "debug", "explain", "optimize", "visualize"

class CodeResponse(BaseModel):
    id: str
    original_code: str
    processed_code: Optional[str] = None
    explanation: str
    visualization_code: Optional[str] = None
    suggestions: List[str] = []
    timestamp: datetime

class ChatMessage(BaseModel):
    message: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    message: str
    response: str
    timestamp: datetime

class ChatHistory(BaseModel):
    id: str
    title: str
    timestamp: datetime
    messages: List[ChatResponse] = []

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/coding_ai_db")

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        await self.init_tables()
    
    async def close(self):
        if self.pool:
            await self.pool.close()
    
    async def init_tables(self):
        async with self.pool.acquire() as conn:
            # Create tables
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS code_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    original_code TEXT NOT NULL,
                    processed_code TEXT,
                    language VARCHAR(50) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    prompt TEXT NOT NULL,
                    explanation TEXT,
                    visualization_code TEXT,
                    suggestions JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    chat_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

# Global database instance
db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.close()

# FastAPI app
app = FastAPI(
    title="Coding AI Agent API",
    description="Backend API for the Coding AI Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In a real app, you'd validate the JWT token here
    # For now, we'll just return a mock user
    return {"user_id": "mock_user", "username": "developer"}

# Simulate AI processing (replace with actual Gemini API calls)
async def process_with_ai(code: str, language: str, action: str, prompt: str) -> dict:
    # Simulate processing delay
    await asyncio.sleep(2)
    
    # Mock responses based on action
    if action == "debug":
        return {
            "processed_code": code.replace("let ", "const "),
            "explanation": f"Found potential issues in your {language} code. Changed 'let' to 'const' for immutable variables.",
            "visualization_code": None,
            "suggestions": [
                "Use const for variables that don't change",
                "Add error handling",
                "Consider using TypeScript for better type safety"
            ]
        }
    elif action == "explain":
        return {
            "processed_code": None,
            "explanation": f"This {language} code implements a sorting algorithm. The time complexity is O(n²) which makes it inefficient for large datasets.",
            "visualization_code": None,
            "suggestions": [
                "Consider using quicksort or mergesort for better performance",
                "Add input validation",
                "Document the algorithm's complexity"
            ]
        }
    elif action == "optimize":
        return {
            "processed_code": f"// Optimized version\n{code}\n// Added performance improvements",
            "explanation": "Optimized the code by reducing unnecessary operations and improving algorithmic complexity.",
            "visualization_code": None,
            "suggestions": [
                "Profile the code to identify bottlenecks",
                "Consider caching frequently accessed data",
                "Use more efficient data structures"
            ]
        }
    elif action == "visualize":
        return {
            "processed_code": None,
            "explanation": "Generated visualization code to help understand the data structure.",
            "visualization_code": f"""// Visualization for {language} code
function visualizeDataStructure() {{
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    // Draw visualization here
    return canvas;
}}""",
            "suggestions": [
                "Interactive visualization helps with understanding",
                "Consider using D3.js for complex visualizations",
                "Add animation to show algorithm steps"
            ]
        }
    else:
        return {
            "processed_code": None,
            "explanation": "Please specify what you'd like me to do with your code.",
            "visualization_code": None,
            "suggestions": []
        }

# API Routes
@app.get("/")
async def root():
    return {"message": "Coding AI Agent API is running"}

@app.post("/process-code", response_model=CodeResponse)
async def process_code(request: CodeRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Process code with AI
        result = await process_with_ai(request.code, request.language, request.action, request.prompt)
        
        # Save to database
        session_id = str(uuid.uuid4())
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO code_sessions (id, original_code, processed_code, language, action, prompt, explanation, visualization_code, suggestions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, session_id, request.code, result["processed_code"], request.language, request.action, 
                request.prompt, result["explanation"], result["visualization_code"], result["suggestions"])
        
        return CodeResponse(
            id=session_id,
            original_code=request.code,
            processed_code=result["processed_code"],
            explanation=result["explanation"],
            visualization_code=result["visualization_code"],
            suggestions=result["suggestions"],
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, current_user: dict = Depends(get_current_user)):
    try:
        # Generate chat response (simulate AI)
        await asyncio.sleep(1)
        response = f"I understand you want to {message.message}. Let me help you with that. Here's what I can do..."
        
        # Create or get chat session
        chat_id = message.chat_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        async with db.pool.acquire() as conn:
            # Create chat session if it doesn't exist
            if not message.chat_id:
                await conn.execute("""
                    INSERT INTO chat_sessions (id, title) VALUES ($1, $2)
                """, chat_id, message.message[:50] + "...")
            
            # Save message
            await conn.execute("""
                INSERT INTO chat_messages (id, chat_id, message, response)
                VALUES ($1, $2, $3, $4)
            """, message_id, chat_id, message.message, response)
        
        return ChatResponse(
            id=message_id,
            message=message.message,
            response=response,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history", response_model=List[ChatHistory])
async def get_chat_history(current_user: dict = Depends(get_current_user)):
    try:
        async with db.pool.acquire() as conn:
            # Get chat sessions
            sessions = await conn.fetch("""
                SELECT id, title, created_at FROM chat_sessions
                ORDER BY created_at DESC
            """)
            
            history = []
            for session in sessions:
                # Get messages for each session
                messages = await conn.fetch("""
                    SELECT id, message, response, created_at FROM chat_messages
                    WHERE chat_id = $1
                    ORDER BY created_at ASC
                """, session['id'])
                
                chat_messages = [
                    ChatResponse(
                        id=str(msg['id']),
                        message=msg['message'],
                        response=msg['response'],
                        timestamp=msg['created_at']
                    ) for msg in messages
                ]
                
                history.append(ChatHistory(
                    id=str(session['id']),
                    title=session['title'],
                    timestamp=session['created_at'],
                    messages=chat_messages
                ))